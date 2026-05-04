import bpy
import uuid

from ..constants import LAYER_TYPE_IMAGE, SOURCE_KIND_IMAGE
from ..repositories.object_repository import get_mv_layer_objects
from .collection_service import move_object_to_collection
from .selection_service import refresh_layer_ui_items, select_layer_by_index


def register_existing_object_as_layer(scene, obj, source_path="", source_kind=SOURCE_KIND_IMAGE, display_name=None):
    layer = obj.mvlt_layer
    layer.is_mv_layer = True
    layer.layer_id = layer.layer_id or uuid.uuid4().hex
    layer.display_name = display_name or obj.name
    layer.layer_type = LAYER_TYPE_IMAGE
    layer.source_path = source_path
    layer.source_kind = source_kind
    layer.frame_start = scene.frame_start
    layer.frame_end = scene.frame_start + scene.mvlt_scene_settings.default_frame_length
    layer.opacity = scene.mvlt_scene_settings.default_opacity
    layer.group_name = scene.mvlt_scene_settings.default_category
    layer.is_locked = False
    layer.is_hidden = obj.hide_viewport
    layer.is_selectable = not obj.hide_select
    layer.layer_order = len(get_mv_layer_objects(scene))
    obj["mvlt_opacity"] = layer.opacity
    move_object_to_collection(scene, obj, layer.group_name)
    refresh_layer_ui_items(scene)
    return obj


def remove_layer(scene, obj):
    name = obj.name
    current_index = scene.mvlt_ui_state.layer_list_index
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    bpy.data.objects.remove(obj, do_unlink=True)
    refresh_layer_ui_items(scene)
    if len(scene.mvlt_ui_state.layer_items) > 0:
        select_layer_by_index(bpy.context, min(current_index, len(scene.mvlt_ui_state.layer_items) - 1))
    return name


def duplicate_layer(scene, obj):
    duplicate = obj.copy()
    duplicate.data = obj.data.copy()
    for collection in obj.users_collection:
        collection.objects.link(duplicate)
    duplicate.name = f"{obj.name}_copy"
    duplicate.animation_data_clear()
    register_existing_object_as_layer(
        scene,
        duplicate,
        source_path=obj.mvlt_layer.source_path,
        source_kind=obj.mvlt_layer.source_kind,
        display_name=f"{obj.mvlt_layer.display_name} Copy",
    )
    duplicate.location.z -= scene.mvlt_import_settings.z_offset_step
    refresh_layer_ui_items(scene)
    for idx, item in enumerate(scene.mvlt_ui_state.layer_items):
        if item.object_name == duplicate.name:
            select_layer_by_index(bpy.context, idx)
            break
    return duplicate


def reorder_layer(scene, obj, direction):
    objects = sorted(get_mv_layer_objects(scene), key=lambda item: item.mvlt_layer.layer_order)
    if obj not in objects:
        return
    index = objects.index(obj)
    target_index = index + direction
    if target_index < 0 or target_index >= len(objects):
        return
    other = objects[target_index]
    obj.mvlt_layer.layer_order, other.mvlt_layer.layer_order = other.mvlt_layer.layer_order, obj.mvlt_layer.layer_order
    refresh_layer_ui_items(scene)


def list_layers(scene):
    return sorted(get_mv_layer_objects(scene), key=lambda item: item.mvlt_layer.layer_order)
