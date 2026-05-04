from ..services import viewport_service
from .modal_ops import MVLT_OT_direct_edit_modal
from .overlay_draw import unregister_overlay_draw_handler


def shutdown_viewport_direct_edit():
    viewport_service.request_stop_with_active_operator()
    unregister_overlay_draw_handler()


__all__ = [
    "MVLT_OT_direct_edit_modal",
    "shutdown_viewport_direct_edit",
]
