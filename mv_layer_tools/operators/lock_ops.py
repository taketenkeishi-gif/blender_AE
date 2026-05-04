from bpy.types import Operator

from ..services.selection_service import get_active_layer_object, refresh_layer_ui_items


class MVLT_OT_toggle_lock(Operator):
    bl_idname = "mvlt.toggle_lock"
    bl_label = "Toggle Lock"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        obj.hide_select = not obj.hide_select
        obj.mvlt_layer.is_locked = obj.hide_select
        obj.mvlt_layer.is_selectable = not obj.hide_select
        refresh_layer_ui_items(context.scene)
        return {"FINISHED"}
