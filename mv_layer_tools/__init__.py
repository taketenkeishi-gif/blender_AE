from .bootstrap import initialize_addon, shutdown_addon
from .registration import register_addon, unregister_addon


bl_info = {
    "name": "MV Layer Tools",
    "author": "OpenAI Codex",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > MVLT",
    "description": "AE-inspired 2D layer workflow tools for Blender MV production",
    "category": "Animation",
}


def register():
    register_addon()
    initialize_addon()


def unregister():
    shutdown_addon()
    unregister_addon()
