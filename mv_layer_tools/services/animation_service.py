from ..utils.fcurve_utils import set_keyframe_interpolation


def insert_transform_keys(obj, frame):
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    obj.keyframe_insert(data_path="scale", frame=frame)
    set_keyframe_interpolation(obj)


def insert_opacity_key(obj, frame):
    obj.keyframe_insert(data_path='["mvlt_opacity"]', frame=frame)
    set_keyframe_interpolation(obj)


def insert_all_primary_keys(obj, frame):
    insert_transform_keys(obj, frame)
    insert_opacity_key(obj, frame)
