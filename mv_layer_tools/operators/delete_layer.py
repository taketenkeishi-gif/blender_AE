from bpy.types import Operator

from ..services.layer_service import remove_layer
from ..services.selection_service import get_active_layer_object


class MVLT_OT_delete_layer(Operator):
    bl_idname = "mvlt.delete_layer"
    bl_label = "Delete Layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        name = remove_layer(context.scene, obj)
        self.report({"INFO"}, f"Deleted layer: {name}")
        return {"FINISHED"}
