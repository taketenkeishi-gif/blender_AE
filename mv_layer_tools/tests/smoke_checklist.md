# Smoke Checklist

- Enable the add-on in Blender 4.x without registration errors.
- Verify the `MVLT` tab appears in the 3D View sidebar.
- Confirm all five tabs are available: Import, Layers, Timeline, Effects, Scene Tools.
- Run `Initialize 2D Scene` and verify an orthographic camera is created.
- Import multiple transparent images and confirm planes plus materials are created.
- Confirm imported layers appear in the Layers UI list.
- Select a layer from the list and verify the active object changes in Blender.
- Toggle visibility and lock from the Layers tab.
- Set frame range and insert primary keys.
- Apply Fade In, Fade Out, and Shake without operator errors.
- Run [blender_addon_regression_test.py](/c:/ポートフォリオ/Blender%20AE%20mode/blender_addon_regression_test.py) in Blender 3.6 background mode and confirm it prints `ALL_TESTS_PASSED`.
