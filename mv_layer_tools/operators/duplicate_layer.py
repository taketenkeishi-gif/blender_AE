from bpy.types import Operator

from ..services.layer_service import duplicate_layer
from ..services.selection_service import get_active_layer_object


class MVLT_OT_duplicate_layer(Operator):
    bl_idname = "mvlt.duplicate_layer"
    bl_label = "Duplicate Layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        duplicate = duplicate_layer(context.scene, obj)
        self.report({"INFO"}, f"Duplicated layer: {duplicate.name}")
        return {"FINISHED"}
