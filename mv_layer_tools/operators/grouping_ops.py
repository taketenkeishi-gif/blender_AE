from bpy.props import StringProperty
from bpy.types import Operator

from ..services.collection_service import move_object_to_collection
from ..services.selection_service import get_active_layer_object, refresh_layer_ui_items


class MVLT_OT_assign_group(Operator):
    bl_idname = "mvlt.assign_group"
    bl_label = "Assign Group"
    bl_options = {"REGISTER", "UNDO"}

    group_name: StringProperty(name="Group", default="General")

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        obj.mvlt_layer.group_name = self.group_name
        move_object_to_collection(context.scene, obj, self.group_name)
        refresh_layer_ui_items(context.scene)
        return {"FINISHED"}
