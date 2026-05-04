from pathlib import Path

import bpy

from .camera_service import ensure_2d_camera
from .layer_service import register_existing_object_as_layer
from .material_service import build_image_material
from .selection_service import refresh_layer_ui_items, select_layer_by_index
from .transform_service import apply_layer_position, orient_plane_to_camera


def _build_plane_mesh(name, width=1.0, height=1.0):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    hw = width / 2.0
    hh = height / 2.0
    vertices = [(-hw, 0.0, -hh), (hw, 0.0, -hh), (hw, 0.0, hh), (-hw, 0.0, hh)]
    faces = [(0, 1, 2, 3)]
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return mesh


def _image_dimensions(image):
    width, height = image.size[:2]
    if not width or not height:
        return 1.0, 1.0
    aspect = width / height
    return (aspect, 1.0) if aspect >= 1.0 else (1.0, 1.0 / aspect)


def build_image_plane(scene, image, path, index, import_settings):
    width, height = _image_dimensions(image)
    name = Path(path).stem
    mesh = _build_plane_mesh(name, width, height)
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    orient_plane_to_camera(obj)
    apply_layer_position(obj, index, import_settings)

    material = build_image_material(image, import_settings.image_alpha_mode)
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

    register_existing_object_as_layer(scene, obj, source_path=path, display_name=name)
    return obj


def import_images(paths, scene_settings, import_settings, scene):
    if scene_settings.use_camera_facing_planes:
        ensure_2d_camera(scene)

    imported = []
    path_list = sorted(paths) if import_settings.sort_mode == "NAME" else list(paths)
    for index, path in enumerate(path_list):
        image = bpy.data.images.load(path, check_existing=True)
        obj = build_image_plane(scene, image, path, index, import_settings)
        imported.append(obj)

    refresh_layer_ui_items(scene)
    if imported:
        select_layer_by_index(bpy.context, len(scene.mvlt_ui_state.layer_items) - 1)
    return imported
