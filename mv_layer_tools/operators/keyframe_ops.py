from bpy.types import Operator

from ..services.animation_service import insert_all_primary_keys, insert_opacity_key, insert_transform_keys
from ..services.selection_service import get_active_layer_object


class MVLT_OT_add_primary_keys(Operator):
    bl_idname = "mvlt.add_primary_keys"
    bl_label = "Add Primary Keys"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        insert_all_primary_keys(get_active_layer_object(context), context.scene.frame_current)
        return {"FINISHED"}


class MVLT_OT_add_transform_keys(Operator):
    bl_idname = "mvlt.add_transform_keys"
    bl_label = "Add Transform Keys"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        insert_transform_keys(get_active_layer_object(context), context.scene.frame_current)
        return {"FINISHED"}


class MVLT_OT_add_opacity_key(Operator):
    bl_idname = "mvlt.add_opacity_key"
    bl_label = "Add Opacity Key"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        insert_opacity_key(get_active_layer_object(context), context.scene.frame_current)
        return {"FINISHED"}
