import bpy

from ..operators.window_ops import MVLT_MT_topbar_menu


def _draw_topbar_menu(self, _context):
    self.layout.menu(MVLT_MT_topbar_menu.bl_idname)


def register_menus():
    try:
        bpy.types.TOPBAR_MT_editor_menus.remove(_draw_topbar_menu)
    except Exception:
        pass
    bpy.types.TOPBAR_MT_editor_menus.append(_draw_topbar_menu)


def unregister_menus():
    try:
        bpy.types.TOPBAR_MT_editor_menus.remove(_draw_topbar_menu)
    except Exception:
        pass
