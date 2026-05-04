import bpy
from bpy.types import Operator

from ..services import viewport_service
from ..viewport.overlay_draw import tag_redraw_all_view3d


class MVLT_OT_start_direct_edit_mode(Operator):
    bl_idname = "mvlt.start_direct_edit_mode"
    bl_label = "Start Direct Edit"
    bl_description = "Start viewport direct edit mode for the active MV layer"

    @classmethod
    def poll(cls, _context):
        return not viewport_service.is_direct_edit_mode_running()

    def execute(self, context):
        viewport_context = viewport_service.find_view3d_window_context(context)
        if viewport_context is None:
            self.report({"ERROR"}, "No 3D Viewport window was found")
            return {"CANCELLED"}

        window, area, region, space = viewport_context
        try:
            with context.temp_override(window=window, area=area, region=region, space_data=space):
                result = bpy.ops.mvlt.direct_edit_modal("INVOKE_DEFAULT")
        except Exception as exc:
            self.report({"ERROR"}, f"Failed to start Direct Edit Mode: {exc}")
            return {"CANCELLED"}

        if "RUNNING_MODAL" not in result:
            self.report({"WARNING"}, "Direct Edit Mode did not start")
            return {"CANCELLED"}
        return {"FINISHED"}


class MVLT_OT_stop_direct_edit_mode(Operator):
    bl_idname = "mvlt.stop_direct_edit_mode"
    bl_label = "Stop Direct Edit"
    bl_description = "Stop viewport direct edit mode"

    @classmethod
    def poll(cls, _context):
        return viewport_service.is_direct_edit_mode_running()

    def execute(self, _context):
        viewport_service.request_stop_with_active_operator()
        tag_redraw_all_view3d()
        return {"FINISHED"}
