from bpy.types import Operator

from ..presets.scene_presets import SCENE_PRESETS
from ..services.camera_service import ensure_2d_camera
from ..services.collection_service import ensure_master_collection
from ..services.selection_service import refresh_layer_ui_items


class MVLT_OT_initialize_scene(Operator):
    bl_idname = "mvlt.initialize_scene"
    bl_label = "Initialize 2D Scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        preset = SCENE_PRESETS["mv_2d"]
        render = context.scene.render
        render.resolution_x = preset["resolution_x"]
        render.resolution_y = preset["resolution_y"]
        render.fps = preset["fps"]
        ensure_master_collection(context.scene)
        ensure_2d_camera(context.scene)
        refresh_layer_ui_items(context.scene)
        self.report({"INFO"}, "Initialized 2D MV scene")
        return {"FINISHED"}


class MVLT_OT_refresh_layers(Operator):
    bl_idname = "mvlt.refresh_layers"
    bl_label = "Refresh Layer List"

    def execute(self, context):
        refresh_layer_ui_items(context.scene)
        return {"FINISHED"}
