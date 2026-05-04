import bpy
import math
import os
import statistics
import time
from pathlib import Path

OUT_DIR = Path(r"C:\ポートフォリオ\Blender AE mode\preview_benchmark")
RESULT_PATH = Path(r"C:\ポートフォリオ\抽出結果.txt")

FRAME_COUNT = 90
WIDTH = 640
HEIGHT = 360
LAYER_COUNT = 40

def log(line):
    with RESULT_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)

def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat

def make_scene():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = FRAME_COUNT
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

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
        except Exception:
            pass

    cam_data = bpy.data.cameras.new("C1_Benchmark_Camera")
    cam = bpy.data.objects.new("C1_Benchmark_Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0.0, -10.0, 0.0)
    cam.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 7.0
    scene.camera = cam

    for i in range(LAYER_COUNT):
        x = ((i % 10) - 4.5) * 0.55
        z = ((i // 10) - 1.5) * 0.55
        bpy.ops.mesh.primitive_plane_add(size=0.48, location=(x, -0.02 * i, z))
        obj = bpy.context.object
        obj.name = "PreviewLayer_%03d" % i
        obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        mat = make_material(
            "PreviewMat_%03d" % i,
            ((i % 7) / 7.0, (i % 11) / 11.0, (i % 5) / 5.0, 1.0),
        )
        obj.data.materials.append(mat)

    light_data = bpy.data.lights.new("C1_Benchmark_Light", "AREA")
    light = bpy.data.objects.new("C1_Benchmark_Light", light_data)
    bpy.context.collection.objects.link(light)
    light.location = (0.0, -4.0, 4.0)
    light.data.energy = 300.0

def animate_frame(frame):
    scene = bpy.context.scene
    scene.frame_set(frame)
    t = frame / max(1, FRAME_COUNT)
    for i, obj in enumerate([o for o in bpy.context.scene.objects if o.name.startswith("PreviewLayer_")]):
        obj.location.x += math.sin(t * math.tau + i * 0.17) * 0.002
        obj.rotation_euler.z = math.sin(t * math.tau + i * 0.13) * 0.02
    bpy.context.view_layer.update()

def run_opengl_preview_benchmark():
    scene = bpy.context.scene
    times = []
    preview_dir = OUT_DIR / "frames"
    preview_dir.mkdir(parents=True, exist_ok=True)

    for old in preview_dir.glob("*.png"):
        try:
            old.unlink()
        except Exception:
            pass

    for frame in range(1, FRAME_COUNT + 1):
        animate_frame(frame)
        scene.render.filepath = str(preview_dir / ("preview_%04d.png" % frame))
        start = time.perf_counter()
        bpy.ops.render.opengl(write_still=True, view_context=False)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    total = sum(times)
    fps = FRAME_COUNT / total if total > 0 else 0.0
    avg_ms = statistics.mean(times) * 1000.0
    med_ms = statistics.median(times) * 1000.0
    max_ms = max(times) * 1000.0
    min_ms = min(times) * 1000.0

    log("=== C1 Preview Benchmark Result ===")
    log("Blender: " + bpy.app.version_string)
    log("Output dir: " + str(preview_dir))
    log("Resolution: %dx%d" % (WIDTH, HEIGHT))
    log("Frame count: %d" % FRAME_COUNT)
    log("Layer count: %d" % LAYER_COUNT)
    log("Total seconds: %.3f" % total)
    log("Preview FPS: %.2f" % fps)
    log("Avg ms/frame: %.2f" % avg_ms)
    log("Median ms/frame: %.2f" % med_ms)
    log("Min ms/frame: %.2f" % min_ms)
    log("Max ms/frame: %.2f" % max_ms)

    if fps >= 30.0:
        log("Judgement: C1 is promising for responsive preview.")
    elif fps >= 15.0:
        log("Judgement: C1 is usable but optimization is needed.")
    elif fps >= 10.0:
        log("Judgement: C1 is borderline.")
    else:
        log("Judgement: C1 is weak at this setting.")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text("=== C1 Preview Benchmark Log ===\n", encoding="utf-8")
    log("Blender exe script started")
    reset_scene()
    make_scene()
    run_opengl_preview_benchmark()
    log("DONE")
    bpy.ops.wm.quit_blender()

main()
