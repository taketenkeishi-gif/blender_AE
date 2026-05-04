from bpy.props import FloatProperty
from bpy.types import Operator

from ..services.effect_service import set_opacity
from ..services.selection_service import get_active_layer_object


class MVLT_OT_set_opacity(Operator):
    bl_idname = "mvlt.set_opacity"
    bl_label = "Set Opacity"
    bl_options = {"REGISTER", "UNDO"}

    value: FloatProperty(name="Opacity", default=1.0, min=0.0, max=1.0)

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        set_opacity(get_active_layer_object(context), self.value)
        return {"FINISHED"}
