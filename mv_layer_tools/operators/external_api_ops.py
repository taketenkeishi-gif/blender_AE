from bpy.types import Operator

from ..services import external_api_server


class MVLT_OT_start_external_api_server(Operator):
    bl_idname = "mvlt.start_external_api_server"
    bl_label = "Start External API"

    def execute(self, _context):
        ok, message = external_api_server.start_server()
        level = {"INFO"} if ok else {"WARNING"}
        self.report(level, message)
        return {"FINISHED"} if ok else {"CANCELLED"}


class MVLT_OT_stop_external_api_server(Operator):
    bl_idname = "mvlt.stop_external_api_server"
    bl_label = "Stop External API"

    def execute(self, _context):
        ok, message = external_api_server.stop_server()
        level = {"INFO"} if ok else {"WARNING"}
        self.report(level, message)
        return {"FINISHED"} if ok else {"CANCELLED"}
