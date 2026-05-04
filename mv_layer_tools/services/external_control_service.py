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
    active_name = ""
    if active is not None and getattr(active, "mvlt_layer", None) and active.mvlt_layer.is_mv_layer:
        active_name = active.mvlt_layer.display_name or active.name
    layers = []
    for obj in _mv_layers(scene):
        layers.append(
            {
                "name": obj.name,
                "display_name": obj.mvlt_layer.display_name or obj.name,
                "layer_order": int(obj.mvlt_layer.layer_order),
                "is_active": bool(active is obj),
                "is_locked": bool(obj.mvlt_layer.is_locked),
                "is_hidden": bool(obj.mvlt_layer.is_hidden),
                "location": {
                    "x": obj.location.x,
                    "y": obj.location.z,
                    "depth": obj.location.y,
                },
            }
        )
    return {
        "layers": layers,
        "active_layer": active_name,
        "direct_edit": get_direct_edit_feedback(),
        "direct_edit_running": is_direct_edit_mode_running(),
    }


def select_layer_by_name(context, object_name):
    scene = context.scene
    target = scene.objects.get(object_name)
    if target is None or not getattr(target, "mvlt_layer", None) or not target.mvlt_layer.is_mv_layer:
        return {"ok": False, "error": "layer not found"}
    if context.mode == "OBJECT":
        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
    context.view_layer.objects.active = target
    sync_selection_from_context(context)
    refresh_layer_ui_items(scene)
    return {"ok": True, "error": ""}


def set_layer_location(context, object_name, x=None, y=None, depth=None):
    scene = context.scene
    target = scene.objects.get(object_name)
    if target is None or not getattr(target, "mvlt_layer", None) or not target.mvlt_layer.is_mv_layer:
        return {"ok": False, "error": "layer not found"}
    if x is not None:
        target.location.x = float(x)
    if y is not None:
        target.location.z = float(y)
    if depth is not None:
        target.location.y = float(depth)
    return {"ok": True, "error": ""}


def get_direct_edit_state(context):
    _ = context
    return {"running": bool(is_direct_edit_mode_running()), "feedback": get_direct_edit_feedback()}
