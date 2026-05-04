from bpy.types import UIList


class MVLT_UL_layer_list(UIList):
    bl_idname = "MVLT_UL_layer_list"

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        outer = layout.column(align=True)
        top = outer.row(align=True)
        op = top.operator("mvlt.select_layer", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
        op.index = index
        top.label(text=item.display_name, icon="IMAGE_DATA")
        top.label(text=item.layer_type)
        top.label(text="", icon="HIDE_ON" if item.is_hidden else "HIDE_OFF")
        top.label(text="", icon="LOCKED" if item.is_locked else "UNLOCKED")

        bottom = outer.row(align=True)
        bottom.label(text=item.timeline_bar, icon="NLA")
        bottom.label(text=item.frame_summary, icon="TIME")
        bottom.label(text=item.group_name or "-", icon="FILE_PARENT")
