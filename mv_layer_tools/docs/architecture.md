# mv_layer_tools Architecture

`mv_layer_tools` is structured so that the Blender UI remains thin while core workflow logic lives in services.

Core boundaries:

- `properties/`: persistent Blender state on `Scene` and `Object`
- `operators/`: Blender entry points, reporting, undo boundaries
- `services/`: import, layer, animation, effect, camera, and selection workflow logic
- `repositories/`: small Blender data access helpers
- `ui/`: N-panel tabs, panel drawing, UIList rendering
- `models/`: lightweight conceptual models that do not depend on Blender API

Implemented first-pass workflow:

1. Initialize a 2D scene and orthographic camera.
2. Import image files as camera-facing planes with alpha materials.
3. Register those planes as managed MV layers.
4. Show them in a UIList and keep selection reasonably synchronized.
5. Edit frame range and insert primary transform / opacity keys.
6. Apply fade, shake, and zoom helpers from the Effects tab.
