from bpy.props import IntProperty
from bpy.types import Operator

from ..services.selection_service import get_active_layer_object
from ..services.timeline_service import jump_to_layer_end, jump_to_layer_start, normalize_frame_range, set_frame_range


class MVLT_OT_set_frame_range(Operator):
    bl_idname = "mvlt.set_frame_range"
    bl_label = "Apply Frame Range"
    bl_options = {"REGISTER", "UNDO"}

    frame_start: IntProperty(name="Start", default=1)
    frame_end: IntProperty(name="End", default=24)

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        set_frame_range(obj, self.frame_start, self.frame_end)
        normalize_frame_range(obj)
        return {"FINISHED"}


class MVLT_OT_jump_to_layer_start(Operator):
    bl_idname = "mvlt.jump_to_layer_start"
    bl_label = "Jump To Start"

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        jump_to_layer_start(context.scene, get_active_layer_object(context))
        return {"FINISHED"}


class MVLT_OT_jump_to_layer_end(Operator):
    bl_idname = "mvlt.jump_to_layer_end"
    bl_label = "Jump To End"

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        jump_to_layer_end(context.scene, get_active_layer_object(context))
        return {"FINISHED"}


class MVLT_OT_nudge_frame(Operator):
    bl_idname = "mvlt.nudge_frame"
    bl_label = "Nudge Frame"

    delta: IntProperty(default=1)

    def execute(self, context):
        scene = context.scene
        scene.frame_current = max(scene.frame_start, min(scene.frame_end, scene.frame_current + self.delta))
        return {"FINISHED"}


class MVLT_OT_set_layer_in_from_current(Operator):
    bl_idname = "mvlt.set_layer_in_from_current"
    bl_label = "Set In From Current"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        set_frame_range(obj, context.scene.frame_current, obj.mvlt_layer.frame_end)
        normalize_frame_range(obj)
        return {"FINISHED"}


class MVLT_OT_set_layer_out_from_current(Operator):
    bl_idname = "mvlt.set_layer_out_from_current"
    bl_label = "Set Out From Current"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_active_layer_object(context) is not None

    def execute(self, context):
        obj = get_active_layer_object(context)
        set_frame_range(obj, obj.mvlt_layer.frame_start, context.scene.frame_current)
        normalize_frame_range(obj)
        return {"FINISHED"}
