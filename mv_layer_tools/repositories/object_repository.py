def get_mv_layer_objects(scene):
    return [obj for obj in scene.objects if getattr(obj, "mvlt_layer", None) and obj.mvlt_layer.is_mv_layer]


def find_object(scene, object_name):
    return scene.objects.get(object_name)
