import importlib
import pathlib
import sys
import traceback

import bpy


ADDONS_DIR = pathlib.Path.home() / "AppData" / "Roaming" / "Blender Foundation" / "Blender" / "3.6" / "scripts" / "addons"
if str(ADDONS_DIR) not in sys.path:
    sys.path.insert(0, str(ADDONS_DIR))


def main():
    module = importlib.import_module("mv_layer_tools")
    print("MODULE_FILE:", pathlib.Path(module.__file__).resolve())
    module.register()
    try:
        print("MENU_CLASS:", hasattr(bpy.types, "MVLT_MT_topbar_menu"))
        print("OP_IMPORT_WINDOW:", hasattr(bpy.ops.mvlt, "open_import_window"))
        print("OP_LAYERS_WINDOW:", hasattr(bpy.ops.mvlt, "open_layers_window"))
        print("OP_TIMELINE_WINDOW:", hasattr(bpy.ops.mvlt, "open_timeline_window"))
        print("OP_EFFECTS_WINDOW:", hasattr(bpy.ops.mvlt, "open_effects_window"))
        print("OP_SCENE_WINDOW:", hasattr(bpy.ops.mvlt, "open_scene_window"))
    finally:
        module.unregister()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("INSTALLED_CHECK_FAILED:", exc)
        traceback.print_exc()
        raise
