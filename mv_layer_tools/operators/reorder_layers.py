from bpy.props import IntProperty
from bpy.types import Operator

from ..services.layer_service import reorder_layer
from ..services.selection_service import get_active_layer_object


class MVLT_OT_reorder_layer(Operator):
    bl_idname = "mvlt.reorder_layer"
    bl_label = "Reorder Layer"
    bl_options = {"REGISTER", "UNDO"}

    direction: IntProperty(default=1)

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        reorder_layer(context.scene, get_active_layer_object(context), self.direction)
        return {"FINISHED"}
