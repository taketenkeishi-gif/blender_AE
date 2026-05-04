from .classes import CLASSES
from .keymaps import register_keymaps, unregister_keymaps
from .menus import register_menus, unregister_menus
from ..properties import register as register_properties, unregister as unregister_properties

import bpy


def register_addon():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    register_properties()
    register_menus()
    register_keymaps()


def unregister_addon():
    unregister_keymaps()
    unregister_menus()
    unregister_properties()
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
