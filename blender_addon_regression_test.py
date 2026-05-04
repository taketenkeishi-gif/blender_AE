import importlib
import pathlib
import shutil
import struct
import sys
import tempfile
import traceback
import zlib

import bpy


ROOT = pathlib.Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def make_png(path, rgba):
    def chunk(tag, data):
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    width = 1
    height = 1
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 6, 0, 0, 0))
    raw = b"\x00" + bytes(rgba)
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    path.write_bytes(signature + ihdr + idat + iend)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    print("ROOT:", ROOT)
    print("BLENDER:", bpy.app.version_string)
    module = importlib.import_module("mv_layer_tools")
    module.register()
    print("REGISTER_OK")

    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="mvlt_regression_", dir=str(ROOT)))
    try:
        image_a = temp_dir / "a_red.png"
        image_b = temp_dir / "b_green.png"
        image_c = temp_dir / "c_blue.png"
        seq_dir = temp_dir / "sequence"
        seq_dir.mkdir()

        make_png(image_a, (255, 0, 0, 255))
        make_png(image_b, (0, 255, 0, 255))
        make_png(image_c, (0, 0, 255, 255))
        make_png(seq_dir / "0001.png", (255, 255, 255, 255))
        make_png(seq_dir / "0002.png", (220, 220, 220, 255))

        scene = bpy.context.scene
        bpy.ops.mvlt.initialize_scene()
        assert_true(scene.camera is not None, "Camera was not initialized")
        assert_true(scene.camera.data.type == "ORTHO", "Camera is not orthographic")
        print("SCENE_INIT_OK")

        imported = module.services.import_service.import_images(
            [str(image_b), str(image_a), str(image_c)],
            scene.mvlt_scene_settings,
            scene.mvlt_import_settings,
            scene,
        )
        assert_true(len(imported) == 3, "Expected 3 imported layers")
        assert_true(len(scene.mvlt_ui_state.layer_items) == 3, "UI layer list did not populate")
        assert_true(scene.mvlt_ui_state.layer_list_index == 2, "Last imported layer was not selected")
        print("IMPORT_OK")

        active = module.services.selection_service.get_active_layer_object(bpy.context)
        assert_true(active is not None, "No active layer after import")
        assert_true(active.mvlt_layer.is_mv_layer, "Imported object is not registered as MV layer")

        bpy.ops.mvlt.select_layer(index=0)
        active = module.services.selection_service.get_active_layer_object(bpy.context)
        assert_true(active.name.startswith("b_green") or active.name.startswith("a_red") or active.name.startswith("c_blue"), "Layer selection failed")
        print("SELECTION_OK")

        active.mvlt_layer.frame_start = 5
        active.mvlt_layer.frame_end = 20
        bpy.ops.mvlt.jump_to_layer_start()
        assert_true(scene.frame_current == 5, "Jump to layer start failed")
        bpy.ops.mvlt.jump_to_layer_end()
        assert_true(scene.frame_current == 20, "Jump to layer end failed")
        bpy.ops.mvlt.add_primary_keys()
        assert_true(active.animation_data is not None and active.animation_data.action is not None, "Primary key insertion failed")
        print("TIMELINE_OK")

        old_hide = active.hide_viewport
        bpy.ops.mvlt.toggle_visibility()
        assert_true(active.hide_viewport != old_hide, "Visibility toggle failed")
        old_lock = active.hide_select
        bpy.ops.mvlt.toggle_lock()
        assert_true(active.hide_select != old_lock, "Lock toggle failed")
        bpy.ops.mvlt.toggle_lock()
        bpy.ops.mvlt.toggle_visibility()
        print("VISIBILITY_LOCK_OK")

        active.mvlt_layer.opacity = 0.65
        bpy.ops.mvlt.set_opacity(value=0.65)
        assert_true(abs(active["mvlt_opacity"] - 0.65) < 1e-6, "Opacity apply failed")
        bpy.ops.mvlt.apply_fade_in()
        bpy.ops.mvlt.apply_fade_out()
        bpy.ops.mvlt.apply_shake()
        bpy.ops.mvlt.apply_zoom()
        assert_true(active.animation_data is not None and active.animation_data.action is not None, "Effect operators did not create animation data")
        print("EFFECTS_OK")

        before_duplicate = len(scene.mvlt_ui_state.layer_items)
        bpy.ops.mvlt.duplicate_layer()
        after_duplicate = len(scene.mvlt_ui_state.layer_items)
        assert_true(after_duplicate == before_duplicate + 1, "Duplicate layer failed")
        print("DUPLICATE_OK")

        bpy.ops.mvlt.reorder_layer(direction=-1)
        bpy.ops.mvlt.reorder_layer(direction=1)
        print("REORDER_OK")

        bpy.ops.mvlt.assign_group(group_name="Foreground")
        active = module.services.selection_service.get_active_layer_object(bpy.context)
        assert_true(active.mvlt_layer.group_name == "Foreground", "Group assign failed")
        print("GROUP_OK")

        op = bpy.ops.mvlt.import_sequence
        result = op("EXEC_DEFAULT", directory=str(seq_dir))
        assert_true("FINISHED" in result, "Sequence import operator failed")
        assert_true(len(scene.mvlt_ui_state.layer_items) >= 5, "Sequence import did not add a layer")
        print("SEQUENCE_OK")

        before_delete = len(scene.mvlt_ui_state.layer_items)
        bpy.ops.mvlt.delete_layer()
        after_delete = len(scene.mvlt_ui_state.layer_items)
        assert_true(after_delete == before_delete - 1, "Delete layer failed")
        print("DELETE_OK")

        print("ALL_TESTS_PASSED")
    finally:
        try:
            module.unregister()
            print("UNREGISTER_OK")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("REGRESSION_FAILED:", exc)
        traceback.print_exc()
        raise
