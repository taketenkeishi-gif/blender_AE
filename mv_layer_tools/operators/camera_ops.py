from bpy.types import Operator

from ..services.camera_service import ensure_2d_camera


class MVLT_OT_init_camera(Operator):
    bl_idname = "mvlt.init_camera"
    bl_label = "Initialize 2D Camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        camera = ensure_2d_camera(context.scene)
        self.report({"INFO"}, f"Ready camera: {camera.name}")
        return {"FINISHED"}
