import bpy

from ..repositories.object_repository import find_object
from ..utils.property_utils import frame_summary, timeline_bar


def refresh_layer_ui_items(scene):
    ui_state = scene.mvlt_ui_state
    items = ui_state.layer_items
    previous_name = None
    if 0 <= ui_state.layer_list_index < len(items):
        previous_name = items[ui_state.layer_list_index].object_name
    items.clear()
    filter_text = (ui_state.layer_filter_text or "").strip().lower()
    layers = sorted(
        [obj for obj in scene.objects if getattr(obj, "mvlt_layer", None) and obj.mvlt_layer.is_mv_layer],
        key=lambda obj: obj.mvlt_layer.layer_order,
    )
    for obj in layers:
        searchable = " ".join(
            [
                obj.name,
                obj.mvlt_layer.display_name or "",
                obj.mvlt_layer.group_name or "",
                obj.mvlt_layer.layer_type or "",
            ]
        ).lower()
        if filter_text and filter_text not in searchable:
            continue
        item = items.add()
        item.object_name = obj.name
        item.display_name = obj.mvlt_layer.display_name or obj.name
        item.layer_type = obj.mvlt_layer.layer_type
        item.frame_summary = frame_summary(obj.mvlt_layer)
        item.group_name = obj.mvlt_layer.group_name
        item.timeline_bar = timeline_bar(scene, obj.mvlt_layer)
        item.is_hidden = obj.mvlt_layer.is_hidden
        item.is_locked = obj.mvlt_layer.is_locked

    active = getattr(bpy.context.view_layer.objects, "active", None)
    if active and getattr(active, "mvlt_layer", None) and active.mvlt_layer.is_mv_layer:
        for idx, item in enumerate(items):
            if item.object_name == active.name:
                ui_state.layer_list_index = idx
                scene.mvlt_scene_settings.active_layer_index = idx
                break
    elif previous_name:
        for idx, item in enumerate(items):
            if item.object_name == previous_name:
                ui_state.layer_list_index = idx
                scene.mvlt_scene_settings.active_layer_index = idx
                break
        else:
            ui_state.layer_list_index = min(ui_state.layer_list_index, len(items) - 1)
            scene.mvlt_scene_settings.active_layer_index = ui_state.layer_list_index
    elif len(items) == 0:
        ui_state.layer_list_index = -1
        scene.mvlt_scene_settings.active_layer_index = -1
    elif ui_state.layer_list_index < 0:
        ui_state.layer_list_index = 0
        scene.mvlt_scene_settings.active_layer_index = 0


def get_active_layer_object(context):
    active = context.view_layer.objects.active
    if active and getattr(active, "mvlt_layer", None) and active.mvlt_layer.is_mv_layer:
        return active
    scene = context.scene
    index = scene.mvlt_ui_state.layer_list_index
    if 0 <= index < len(scene.mvlt_ui_state.layer_items):
        item = scene.mvlt_ui_state.layer_items[index]
        return find_object(scene, item.object_name)
    return None


def select_layer_by_index(context, index):
    scene = context.scene
    if index < 0 or index >= len(scene.mvlt_ui_state.layer_items):
        return None
    item = scene.mvlt_ui_state.layer_items[index]
    obj = find_object(scene, item.object_name)
    if obj is None:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj
    scene.mvlt_ui_state.layer_list_index = index
    scene.mvlt_scene_settings.active_layer_index = index
    return obj


def sync_selection_from_context(context):
    scene = getattr(context, "scene", None)
    if scene is None or not hasattr(scene, "mvlt_ui_state"):
        return
    active = getattr(context.view_layer.objects, "active", None)
    if active and getattr(active, "mvlt_layer", None) and active.mvlt_layer.is_mv_layer:
        for idx, item in enumerate(scene.mvlt_ui_state.layer_items):
            if item.object_name == active.name:
                scene.mvlt_ui_state.layer_list_index = idx
                scene.mvlt_scene_settings.active_layer_index = idx
                break
    elif len(scene.mvlt_ui_state.layer_items) == 0:
        scene.mvlt_ui_state.layer_list_index = -1
        scene.mvlt_scene_settings.active_layer_index = -1
