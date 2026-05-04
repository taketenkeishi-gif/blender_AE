from math import radians

import bpy

from ..constants import CAMERA_NAME


def ensure_2d_camera(scene):
    camera_obj = scene.objects.get(CAMERA_NAME)
    if camera_obj is None:
        camera_data = bpy.data.cameras.new(CAMERA_NAME)
        camera_obj = bpy.data.objects.new(CAMERA_NAME, camera_data)
        scene.collection.objects.link(camera_obj)
    camera_obj.location = (0.0, -10.0, 0.0)
    camera_obj.rotation_euler = (radians(90.0), 0.0, 0.0)
    camera_obj.data.type = "ORTHO"
    camera_obj.data.ortho_scale = 10.0
    scene.camera = camera_obj
    return camera_obj
