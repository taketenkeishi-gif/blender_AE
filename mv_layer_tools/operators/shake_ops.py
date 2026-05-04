from bpy.types import Operator

from ..services.effect_service import apply_shake
from ..services.selection_service import get_active_layer_object


class MVLT_OT_apply_shake(Operator):
    bl_idname = "mvlt.apply_shake"
    bl_label = "Apply Shake"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        settings = context.scene.mvlt_effect_settings
        apply_shake(
            obj,
            obj.mvlt_layer.frame_start,
            obj.mvlt_layer.frame_end,
            settings.shake_default_strength,
            settings.shake_default_speed,
        )
        return {"FINISHED"}
