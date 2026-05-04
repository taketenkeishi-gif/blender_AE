from math import radians


def orient_plane_to_camera(obj):
    obj.rotation_euler = (radians(90.0), 0.0, 0.0)


def apply_layer_position(obj, index, import_settings):
    if import_settings.place_mode == "LINE_X":
        obj.location = (index * 1.2, 0.0, 0.0)
    else:
        obj.location = (0.0, 0.0, -(index * import_settings.z_offset_step))
