import json
import math
import os
import time
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

WORK_DIR = Path(r"C:\mvlt_c1_live")
PREVIEW_TMP = WORK_DIR / "preview_tmp.jpg"
PREVIEW_FILE = WORK_DIR / "preview.jpg"
STATE_TMP = WORK_DIR / "state_tmp.json"
STATE_FILE = WORK_DIR / "state.json"
COMMAND_FILE = WORK_DIR / "command.json"
STOP_FILE = WORK_DIR / "stop.txt"

WIDTH = 640
HEIGHT = 360
ORTHO_SCALE = 7.0

ACTIVE_TARGET_FPS = 24.0
IDLE_TARGET_FPS = 6.0
JPEG_QUALITY = 40

LAYER_ID = "layer_001"
LAYER_NAME = "Drag Test Layer"
PLANE_WIDTH = 2.2
PLANE_HEIGHT = 1.25

_last_command_mtime = None
_last_command_seq = -1
_layer_obj = None
_frame_index = 0
_last_command_time = 0.0
_last_render_ms = 0.0

def safe_replace(src: Path, dst: Path, retries=12, delay=0.004):
    for _ in range(retries):
        try:
            os.replace(src, dst)
            return True
        except PermissionError:
            time.sleep(delay)
        except FileNotFoundError:
            return False
    return False

def write_json_atomic(path: Path, tmp: Path, data):
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    safe_replace(tmp, path)

def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat

def setup_scene():
    global _layer_obj

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if STOP_FILE.exists():
        STOP_FILE.unlink()

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 240
    scene.frame_current = 1
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = JPEG_QUALITY

    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        pass

    if hasattr(scene, "eevee"):
        try:
            scene.eevee.taa_render_samples = 1
            scene.eevee.taa_samples = 1
            scene.eevee.use_gtao = False
            scene.eevee.use_bloom = False
            scene.eevee.use_soft_shadows = False
        except Exception:
            pass

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    try:
        world.color = (0.035, 0.035, 0.04)
    except Exception:
        pass

    cam_data = bpy.data.cameras.new("C1_Camera")
    cam = bpy.data.objects.new("C1_Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0.0, -10.0, 0.0)
    cam.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ORTHO_SCALE
    scene.camera = cam

    grid_mat = create_material("C1_Grid_Mat", (0.10, 0.10, 0.12, 1.0))
    for i in range(-6, 7):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(i * 0.5, 0.03, 0.0))
        line = bpy.context.object
        line.name = "GridV_%02d" % (i + 6)
        line.dimensions = (0.012, 0.01, ORTHO_SCALE)
        line.data.materials.append(grid_mat)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.035, i * 0.5))
        line = bpy.context.object
        line.name = "GridH_%02d" % (i + 6)
        line.dimensions = (ORTHO_SCALE * WIDTH / HEIGHT, 0.01, 0.012)
        line.data.materials.append(grid_mat)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = LAYER_ID
    obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    obj.scale = (PLANE_WIDTH, PLANE_HEIGHT, 1.0)
    mat = create_material("C1_Layer_Mat", (0.1, 0.45, 1.0, 1.0))
    obj.data.materials.append(mat)
    _layer_obj = obj

    light_data = bpy.data.lights.new("C1_Light", "AREA")
    light = bpy.data.objects.new("C1_Light", light_data)
    bpy.context.collection.objects.link(light)
    light.location = (0.0, -4.0, 4.0)
    light.data.energy = 300.0

    bpy.context.view_layer.update()

def world_extent():
    world_h = ORTHO_SCALE
    world_w = ORTHO_SCALE * (WIDTH / HEIGHT)
    return world_w, world_h

def object_screen_rect(obj):
    scene = bpy.context.scene
    cam = scene.camera

    coords = []
    for corner in obj.bound_box:
        world = obj.matrix_world @ Vector(corner)
        co = world_to_camera_view(scene, cam, world)
        coords.append(co)

    xs = [max(0.0, min(1.0, c.x)) for c in coords]
    ys = [max(0.0, min(1.0, 1.0 - c.y)) for c in coords]

    x1 = min(xs)
    x2 = max(xs)
    y1 = min(ys)
    y2 = max(ys)

    return {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "cx": (x1 + x2) * 0.5,
        "cy": (y1 + y2) * 0.5,
    }

def build_state():
    world_w, world_h = world_extent()
    x = float(_layer_obj.location.x)
    z = float(_layer_obj.location.z)
    return {
        "preview": {
            "width": WIDTH,
            "height": HEIGHT,
            "ortho_scale": ORTHO_SCALE,
            "world_width": world_w,
            "world_height": world_h,
            "jpeg_quality": JPEG_QUALITY,
        },
        "camera": {"type": "ORTHO", "x": 0.0, "y": -10.0, "z": 0.0},
        "layers": [
            {
                "id": LAYER_ID,
                "name": LAYER_NAME,
                "x": x,
                "z": z,
                "y": float(_layer_obj.location.y),
                "width": PLANE_WIDTH,
                "height": PLANE_HEIGHT,
                "rotation_z": float(_layer_obj.rotation_euler.z),
                "screen_rect": object_screen_rect(_layer_obj),
                "locked": False,
                "visible": True,
            }
        ],
        "frame": _frame_index,
        "updated_at": time.time(),
        "last_command_at": _last_command_time,
        "last_render_ms": _last_render_ms,
    }

def read_latest_command():
    global _last_command_mtime
    if not COMMAND_FILE.exists():
        return None

    try:
        mtime = COMMAND_FILE.stat().st_mtime
    except FileNotFoundError:
        return None

    if _last_command_mtime is not None and mtime <= _last_command_mtime:
        return None

    _last_command_mtime = mtime

    try:
        return json.loads(COMMAND_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        print("[C1] command read failed:", exc)
        return None

def apply_command_if_any():
    global _last_command_seq, _last_command_time

    data = read_latest_command()
    if not data:
        return False

    seq = int(data.get("seq", -1))
    if seq >= 0 and seq <= _last_command_seq:
        return False

    if seq >= 0:
        _last_command_seq = seq

    if data.get("type") == "set_transform" and data.get("layer_id") == LAYER_ID:
        x = float(data.get("x", _layer_obj.location.x))
        z = float(data.get("z", _layer_obj.location.z))
        _layer_obj.location.x = x
        _layer_obj.location.z = z

        if "rotation_z" in data:
            _layer_obj.rotation_euler.z = float(data["rotation_z"])

        bpy.context.view_layer.update()
        _last_command_time = time.time()
        return True

    return False

def render_preview():
    global _last_render_ms

    scene = bpy.context.scene
    scene.render.filepath = str(PREVIEW_TMP)

    start = time.perf_counter()
    bpy.ops.render.opengl(write_still=True, view_context=False)
    _last_render_ms = (time.perf_counter() - start) * 1000.0

    safe_replace(PREVIEW_TMP, PREVIEW_FILE)

def main_loop():
    global _frame_index

    print("[C1] backend v3 started")

    render_preview()
    write_json_atomic(STATE_FILE, STATE_TMP, build_state())

    active_dt = 1.0 / ACTIVE_TARGET_FPS
    idle_dt = 1.0 / IDLE_TARGET_FPS
    last_idle_render = time.perf_counter()

    while not STOP_FILE.exists():
        start = time.perf_counter()
        _frame_index += 1

        changed = apply_command_if_any()
        now = time.perf_counter()

        if changed:
            render_preview()
            write_json_atomic(STATE_FILE, STATE_TMP, build_state())
            last_idle_render = time.perf_counter()
        else:
            if now - last_idle_render >= idle_dt:
                render_preview()
                write_json_atomic(STATE_FILE, STATE_TMP, build_state())
                last_idle_render = time.perf_counter()

        elapsed = time.perf_counter() - start
        if changed:
            time.sleep(max(0.001, active_dt - elapsed))
        else:
            time.sleep(0.004)

    print("[C1] stop requested")
    bpy.ops.wm.quit_blender()

def main():
    reset_scene()
    setup_scene()
    main_loop()

main()
