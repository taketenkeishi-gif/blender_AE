from bpy.types import Operator

from ..services.effect_service import apply_zoom
from ..services.selection_service import get_active_layer_object


class MVLT_OT_apply_zoom(Operator):
    bl_idname = "mvlt.apply_zoom"
    bl_label = "Apply Zoom"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        amount = context.scene.mvlt_effect_settings.zoom_default_amount
        apply_zoom(obj, obj.mvlt_layer.frame_start, obj.mvlt_layer.frame_end, amount)
        return {"FINISHED"}
