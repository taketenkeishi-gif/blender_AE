import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from bpy_extras import view3d_utils

from ..services import viewport_service
from .hit_test import project_bound_box_to_region_rect


_DRAW_HANDLE = None


def _draw_line_strip(coords, color, width=2.0):
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINE_STRIP", {"pos": coords})
    gpu.state.blend_set("ALPHA")
    gpu.state.line_width_set(width)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set("NONE")


def _draw_lines(coords, color, width=1.5):
    shader = gpu.shader.from_builtin("2D_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": coords})
    gpu.state.blend_set("ALPHA")
    gpu.state.line_width_set(width)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set("NONE")


def _draw_text_line(text, x, y, rgba):
    font_id = 0
    blf.size(font_id, 14, 72)
    blf.position(font_id, x, y, 0)
    blf.color(font_id, rgba[0], rgba[1], rgba[2], rgba[3])
    blf.draw(font_id, text)


def draw_direct_edit_overlay():
    if not viewport_service.is_direct_edit_mode_running():
        return

    context = bpy.context
    area = getattr(context, "area", None)
    if area is None or area.type != "VIEW_3D":
        return

    feedback = viewport_service.get_direct_edit_feedback()
    obj = viewport_service.get_active_mv_layer(context)
    if obj is None:
        _draw_text_line("Direct Edit Mode: ON (No active MV layer)", 18, 42, (1.0, 0.9, 0.4, 1.0))
        _draw_text_line(feedback.get("message", ""), 18, 22, (0.8, 0.92, 1.0, 1.0))
        return

    rect = project_bound_box_to_region_rect(context, obj)
    if rect is not None:
        x1, y1, x2, y2 = rect
        border = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
        _draw_line_strip(border, (1.0, 0.82, 0.18, 1.0), width=2.5)

    region = getattr(context, "region", None)
    space_data = getattr(context, "space_data", None)
    rv3d = getattr(space_data, "region_3d", None)
    if region is not None and rv3d is not None:
        center = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector(obj.location))
        if center is not None:
            cx, cy = center.x, center.y
            cross = [(cx - 6, cy), (cx + 6, cy), (cx, cy - 6), (cx, cy + 6)]
            _draw_lines(cross, (0.35, 0.95, 1.0, 1.0), width=1.75)

    # Temporary mapping for 2D MVP:
    # UI X -> object.location.x, UI Y -> object.location.z, UI depth -> object.location.y
    state = feedback.get("state", "Ready")
    target = feedback.get("target", "")
    message = feedback.get("message", "")
    _draw_text_line(f"Direct Edit Mode: {state}", 18, 64, (1.0, 1.0, 1.0, 1.0))
    _draw_text_line(f"Active: {obj.mvlt_layer.display_name or obj.name}", 18, 44, (0.8, 0.92, 1.0, 1.0))
    if target:
        _draw_text_line(f"Target: {target}", 18, 24, (1.0, 0.9, 0.4, 1.0))
    else:
        _draw_text_line(message, 18, 24, (0.8, 0.92, 1.0, 1.0))
    _draw_text_line(
        f"Pos X:{obj.location.x:.3f}  Y:{obj.location.z:.3f}  Depth:{obj.location.y:.3f}",
        18,
        8,
        (0.8, 0.92, 1.0, 1.0),
    )


def register_overlay_draw_handler():
    global _DRAW_HANDLE
    if _DRAW_HANDLE is not None:
        return
    _DRAW_HANDLE = bpy.types.SpaceView3D.draw_handler_add(draw_direct_edit_overlay, (), "WINDOW", "POST_PIXEL")


def unregister_overlay_draw_handler():
    global _DRAW_HANDLE
    if _DRAW_HANDLE is None:
        return
    bpy.types.SpaceView3D.draw_handler_remove(_DRAW_HANDLE, "WINDOW")
    _DRAW_HANDLE = None


def tag_redraw_all_view3d():
    window_manager = getattr(bpy.context, "window_manager", None)
    if window_manager is None:
        return
    for window in window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()