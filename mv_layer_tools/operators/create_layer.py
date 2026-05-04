from bpy.types import Operator

from ..services.layer_service import register_existing_object_as_layer


class MVLT_OT_register_selected_as_layer(Operator):
    bl_idname = "mvlt.register_selected_as_layer"
    bl_label = "Register Selected As Layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        register_existing_object_as_layer(context.scene, context.active_object, display_name=context.active_object.name)
        self.report({"INFO"}, "Selected object registered as MV layer")
        return {"FINISHED"}
