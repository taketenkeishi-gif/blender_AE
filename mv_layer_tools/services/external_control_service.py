import bpy

from .selection_service import refresh_layer_ui_items, sync_selection_from_context
from .viewport_service import get_direct_edit_feedback, is_direct_edit_mode_running


def _mv_layers(scene):
    layers = [
        obj
        for obj in scene.objects
        if getattr(obj, "mvlt_layer", None) and obj.mvlt_layer.is_mv_layer
    ]
    layers.sort(key=lambda obj: getattr(obj.mvlt_layer, "layer_order", 0))
    return layers


def get_layer_state(context):
    scene = context.scene
    active = getattr(context.view_layer.objects, "active", None)
    layers = []
    for obj in _mv_layers(scene):
        layers.append(
            {
                "name": obj.name,
                "display_name": obj.mvlt_layer.display_name or obj.name,
                "location": {
                    "x": float(obj.location.x),
                    "y": float(obj.location.z),
                    "depth": float(obj.location.y),
                },
                "selected": bool(obj.select_get()),
                "active": bool(active is obj),
            }
        )
    return {"layers": layers}


def select_layer_by_name(context, name):
    scene = context.scene
    target = scene.objects.get(name)
    if target is None or not getattr(target, "mvlt_layer", None) or not target.mvlt_layer.is_mv_layer:
        return False, "Layer not found"
    if context.mode == "OBJECT":
        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
    context.view_layer.objects.active = target
    sync_selection_from_context(context)
    refresh_layer_ui_items(scene)
    return True, "OK"


def set_layer_location(context, name, x=None, y=None, depth=None):
    scene = context.scene
    target = scene.objects.get(name)
    if target is None or not getattr(target, "mvlt_layer", None) or not target.mvlt_layer.is_mv_layer:
        return False, "Layer not found"
    if x is not None:
        target.location.x = float(x)
    if y is not None:
        target.location.z = float(y)
    if depth is not None:
        target.location.y = float(depth)
    return True, "OK"


def get_direct_edit_state(_context):
    feedback = get_direct_edit_feedback()
    return {
        "running": bool(is_direct_edit_mode_running()),
        "state": feedback.get("state", ""),
        "target": feedback.get("target", ""),
        "message": feedback.get("message", ""),
    }
