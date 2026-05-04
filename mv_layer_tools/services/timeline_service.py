def set_frame_range(obj, start, end):
    layer = obj.mvlt_layer
    layer.frame_start = min(start, end)
    layer.frame_end = max(start, end)


def normalize_frame_range(obj):
    layer = obj.mvlt_layer
    if layer.frame_end < layer.frame_start:
        layer.frame_end = layer.frame_start


def jump_to_layer_start(scene, obj):
    scene.frame_current = obj.mvlt_layer.frame_start


def jump_to_layer_end(scene, obj):
    scene.frame_current = obj.mvlt_layer.frame_end
