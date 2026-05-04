from bpy.props import IntProperty
from bpy.types import Operator

from ..services.selection_service import select_layer_by_index


class MVLT_OT_select_layer(Operator):
    bl_idname = "mvlt.select_layer"
    bl_label = "Select Layer"
    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty(default=-1)

    def execute(self, context):
        obj = select_layer_by_index(context, self.index)
        if obj is None:
            self.report({"ERROR"}, "Layer not found")
            return {"CANCELLED"}
        return {"FINISHED"}
