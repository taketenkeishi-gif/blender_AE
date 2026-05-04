from bpy.types import Operator

from ..services.selection_service import get_active_layer_object, refresh_layer_ui_items


class MVLT_OT_toggle_visibility(Operator):
    bl_idname = "mvlt.toggle_visibility"
    bl_label = "Toggle Visibility"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        obj.hide_viewport = not obj.hide_viewport
        obj.hide_render = obj.hide_viewport
        obj.mvlt_layer.is_hidden = obj.hide_viewport
        refresh_layer_ui_items(context.scene)
        return {"FINISHED"}
