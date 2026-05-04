from mathutils import Vector
from bpy_extras import view3d_utils


def mouse_to_world(context, mouse_xy, depth_location):
    region = getattr(context, "region", None)
    space_data = getattr(context, "space_data", None)
    rv3d = getattr(space_data, "region_3d", None)
    if region is None or rv3d is None:
        return None

    if isinstance(depth_location, Vector):
        depth_ref = depth_location
    else:
        depth_ref = Vector(depth_location)
    return view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_xy, depth_ref)


def delta_from_world_anchor(context, mouse_xy, depth_location, world_anchor):
    if world_anchor is None:
        return None
    current_world = mouse_to_world(context, mouse_xy, depth_location)
    if current_world is None:
        return None
    return current_world - world_anchor
