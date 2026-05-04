from bpy.types import Operator

from ..services import viewport_service
from . import transform_mapper
from .overlay_draw import register_overlay_draw_handler, tag_redraw_all_view3d, unregister_overlay_draw_handler


class MVLT_OT_direct_edit_modal(Operator):
    bl_idname = "mvlt.direct_edit_modal"
    bl_label = "MVLT Direct Edit Modal"
    bl_options = {"INTERNAL"}

    def __init__(self):
        self.dragging = False
        self.target_obj = None
        self.start_location = None
        self.start_world = None
        self._timer = None
        self._external_stop_requested = False
        self._cleaned = False

    def request_external_stop(self):
        self._external_stop_requested = True

    def force_shutdown(self, context):
        self._cleanup(context)

    def invoke(self, context, _event):
        if context.area is None or context.area.type != "VIEW_3D":
            self.report({"WARNING"}, "Run Direct Edit Mode inside a 3D View")
            return {"CANCELLED"}
        if context.region is None or context.region.type != "WINDOW":
            self.report({"WARNING"}, "Direct Edit Mode must run in the viewport window region")
            return {"CANCELLED"}
        if viewport_service.is_direct_edit_mode_running():
            self.report({"INFO"}, "Direct Edit Mode is already running")
            return {"CANCELLED"}

        viewport_service.set_modal_operator(self)
        register_overlay_draw_handler()
        tag_redraw_all_view3d()

        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "Direct Edit Mode started")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if self._should_stop(event):
            self._cleanup(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            return {"RUNNING_MODAL"}

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE", "WHEELINMOUSE", "WHEELOUTMOUSE"}:
            return {"PASS_THROUGH"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            return self._handle_left_mouse_press(context, event)

        if event.type == "MOUSEMOVE" and self.dragging:
            if self._handle_mouse_move(context, event):
                return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.dragging:
            self.dragging = False
            self.target_obj = None
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def cancel(self, context):
        self._cleanup(context)

    def _should_stop(self, event):
        if event.type == "ESC":
            return True
        if self._external_stop_requested:
            return True
        if viewport_service.consume_stop_request():
            return True
        if not viewport_service.is_direct_edit_mode_running():
            return True
        return False

    def _handle_left_mouse_press(self, context, event):
        mouse_x = event.mouse_region_x
        mouse_y = event.mouse_region_y
        obj, _ = viewport_service.find_editable_layer_at_screen_point(context, mouse_x, mouse_y, padding=10)
        if obj is None:
            return {"PASS_THROUGH"}

        viewport_service.select_as_active_layer(context, obj)
        self.dragging = True
        self.target_obj = obj
        self.start_location = obj.location.copy()
        self.start_world = transform_mapper.mouse_to_world(context, (mouse_x, mouse_y), self.start_location)
        return {"RUNNING_MODAL"}

    def _handle_mouse_move(self, context, event):
        if self.target_obj is None:
            return False
        delta = transform_mapper.delta_from_world_anchor(
            context,
            (event.mouse_region_x, event.mouse_region_y),
            self.start_location,
            self.start_world,
        )
        if delta is None:
            return False

        viewport_service.apply_screen_plane_drag(self.target_obj, self.start_location, delta)
        if context.area is not None:
            context.area.tag_redraw()
        tag_redraw_all_view3d()
        return True

    def _cleanup(self, context):
        if self._cleaned:
            return
        self._cleaned = True

        self.dragging = False
        self.target_obj = None
        self.start_location = None
        self.start_world = None

        window_manager = getattr(context, "window_manager", None)
        if self._timer is not None and window_manager is not None:
            try:
                window_manager.event_timer_remove(self._timer)
            except Exception:
                pass
        self._timer = None

        unregister_overlay_draw_handler()
        viewport_service.clear_modal_operator(self)
        tag_redraw_all_view3d()