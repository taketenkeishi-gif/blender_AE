import bpy


def get_material(name):
    return bpy.data.materials.get(name)


def new_material(name):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    return material
