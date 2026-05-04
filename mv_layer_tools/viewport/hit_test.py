from mathutils import Vector
from bpy_extras import view3d_utils


def project_bound_box_to_region_rect(context, obj):
    region = getattr(context, "region", None)
    space_data = getattr(context, "space_data", None)
    rv3d = getattr(space_data, "region_3d", None)
    if region is None or rv3d is None or obj is None:
        return None

    points = []
    for corner in obj.bound_box:
        world_corner = obj.matrix_world @ Vector(corner)
        screen_point = view3d_utils.location_3d_to_region_2d(region, rv3d, world_corner)
        if screen_point is not None:
            points.append(screen_point)

    if not points:
        return None

    xs = [point.x for point in points]
    ys = [point.y for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def point_in_rect(mouse_x, mouse_y, rect, padding=8):
    min_x, min_y, max_x, max_y = rect
    return (min_x - padding) <= mouse_x <= (max_x + padding) and (min_y - padding) <= mouse_y <= (max_y + padding)


def hit_test_layer_bounds(context, obj, mouse_x, mouse_y, padding=8):
    rect = project_bound_box_to_region_rect(context, obj)
    if rect is None:
        return False, None
    return point_in_rect(mouse_x, mouse_y, rect, padding=padding), rect
