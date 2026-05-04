import bpy


def get_collection(name):
    return bpy.data.collections.get(name)


def ensure_collection(name, parent_collection=None):
    collection = get_collection(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        if parent_collection:
            parent_collection.children.link(collection)
    elif parent_collection and parent_collection.children.get(collection.name) is None:
        parent_collection.children.link(collection)
    return collection
