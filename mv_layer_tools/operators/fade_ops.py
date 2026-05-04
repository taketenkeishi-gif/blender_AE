from bpy.types import Operator

from ..services.effect_service import apply_fade_in, apply_fade_out
from ..services.selection_service import get_active_layer_object


class MVLT_OT_apply_fade_in(Operator):
    bl_idname = "mvlt.apply_fade_in"
    bl_label = "Fade In"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        duration = context.scene.mvlt_effect_settings.fade_default_duration
        apply_fade_in(obj, obj.mvlt_layer.frame_start, duration)
        return {"FINISHED"}


class MVLT_OT_apply_fade_out(Operator):
    bl_idname = "mvlt.apply_fade_out"
    bl_label = "Fade Out"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        duration = context.scene.mvlt_effect_settings.fade_default_duration
        apply_fade_out(obj, obj.mvlt_layer.frame_end, duration)
        return {"FINISHED"}
