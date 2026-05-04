import bpy
from mathutils import Vector

from .selection_service import get_active_layer_object, sync_selection_from_context


_MODAL_OPERATOR = None
_DIRECT_EDIT_RUNNING = False
_STOP_REQUESTED = False
_DIRECT_EDIT_FEEDBACK = {
    "state": "Stopped",
    "target": "",
    "message": "Direct Edit Mode is stopped",
}


def _layer_display_name(obj):
    if obj is None:
        return ""
    layer = getattr(obj, "mvlt_layer", None)
    if layer is not None:
        return layer.display_name or obj.name
    return obj.name


def set_direct_edit_feedback(state=None, target_obj=None, message=None):
    if state is not None:
        _DIRECT_EDIT_FEEDBACK["state"] = state
    if target_obj is not None:
        _DIRECT_EDIT_FEEDBACK["target"] = _layer_display_name(target_obj)
    elif target_obj is None and state in {"Stopped", "Ready", "No Hit"}:
        _DIRECT_EDIT_FEEDBACK["target"] = ""
    if message is not None:
        _DIRECT_EDIT_FEEDBACK["message"] = message


def get_direct_edit_feedback():
    return dict(_DIRECT_EDIT_FEEDBACK)


def set_modal_operator(operator):
    global _MODAL_OPERATOR, _DIRECT_EDIT_RUNNING, _STOP_REQUESTED
    _MODAL_OPERATOR = operator
    _DIRECT_EDIT_RUNNING = True
    _STOP_REQUESTED = False
    set_direct_edit_feedback(
        state="Ready",
        message="Left-drag an editable MV Layer in the viewport",
    )


def clear_modal_operator(operator=None):
    global _MODAL_OPERATOR, _DIRECT_EDIT_RUNNING, _STOP_REQUESTED
    if operator is None or _MODAL_OPERATOR is operator:
        _MODAL_OPERATOR = None
        _DIRECT_EDIT_RUNNING = False
        _STOP_REQUESTED = False
        set_direct_edit_feedback(
            state="Stopped",
            message="Direct Edit Mode is stopped",
        )


def get_modal_operator():
    return _MODAL_OPERATOR


def is_direct_edit_mode_running():
    return _DIRECT_EDIT_RUNNING


def request_stop_direct_edit_mode():
    global _STOP_REQUESTED
    _STOP_REQUESTED = True


def consume_stop_request():
    global _STOP_REQUESTED
    if not _STOP_REQUESTED:
        return False
    _STOP_REQUESTED = False
    return True


def request_stop_with_active_operator():
    request_stop_direct_edit_mode()
    operator = get_modal_operator()
    if operator is None:
        return
    if hasattr(operator, "request_external_stop"):
        operator.request_external_stop()
    if hasattr(operator, "force_shutdown"):
        operator.force_shutdown(bpy.context)


def is_managed_mv_layer(obj):
    return bool(obj and getattr(obj, "mvlt_layer", None) and obj.mvlt_layer.is_mv_layer)


def is_layer_editable(obj):
    if not is_managed_mv_layer(obj):
        return False
    if obj.mvlt_layer.is_locked or obj.hide_select:
        return False
    if obj.mvlt_layer.is_hidden or obj.hide_viewport:
        return False
    return True


def get_active_mv_layer(context):
    obj = get_active_layer_object(context)
    if not is_managed_mv_layer(obj):
        return None
    return obj


def get_active_editable_layer(context):
    obj = get_active_mv_layer(context)
    if not is_layer_editable(obj):
        return None
    return obj


def get_editable_layers(context):
    scene = getattr(context, "scene", None)
    if scene is None:
        return []
    layers = [obj for obj in scene.objects if is_layer_editable(obj)]
    layers.sort(key=lambda obj: getattr(obj.mvlt_layer, "layer_order", 0), reverse=True)
    return layers


def find_editable_layer_at_screen_point(context, mouse_x, mouse_y, padding=10):
    from ..viewport import hit_test

    return hit_test.hit_test_topmost_layer_bounds(
        context,
        get_editable_layers(context),
        mouse_x,
        mouse_y,
        padding=padding,
    )


def select_as_active_layer(context, obj):
    if obj is None:
        return
    if context.mode == "OBJECT":
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
    context.view_layer.objects.active = obj
    sync_selection_from_context(context)


def apply_screen_plane_drag(obj, start_location, delta):
    if obj is None or start_location is None or delta is None:
        return

    # Temporary coordinate mapping for MVP:
    # UI X -> object.location.x
    # UI Y -> object.location.z
    # UI depth -> object.location.y
    next_location = Vector(start_location)
    next_location.x = start_location.x + delta.x
    next_location.z = start_location.z + delta.z
    next_location.y = start_location.y
    obj.location = next_location


def find_view3d_window_context(context):
    window_manager = getattr(bpy.context, "window_manager", None)
    if window_manager is None:
        return None

    preferred = []
    active_window = getattr(context, "window", None)
    if active_window is not None:
        preferred.append(active_window)
    preferred.extend([window for window in window_manager.windows if window not in preferred])

    for window in preferred:
        screen = window.screen
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region is None:
                continue
            space = next((item for item in area.spaces if item.type == "VIEW_3D"), None)
            if space is None:
                continue
            return window, area, region, space
    return None