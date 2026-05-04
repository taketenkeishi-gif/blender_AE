from ..constants import MASTER_COLLECTION_NAME
from ..repositories.collection_repository import ensure_collection


def ensure_master_collection(scene):
    name = scene.mvlt_scene_settings.master_collection_name if hasattr(scene, "mvlt_scene_settings") else MASTER_COLLECTION_NAME
    return ensure_collection(name, scene.collection)


def ensure_category_collection(scene, category_name):
    master = ensure_master_collection(scene)
    return ensure_collection(category_name or "General", master)


def move_object_to_collection(scene, obj, category_name):
    target = ensure_category_collection(scene, category_name)
    for collection in list(obj.users_collection):
        if collection != target:
            collection.objects.unlink(obj)
    if obj.name not in target.objects:
        target.objects.link(obj)
    return target
