# Future Fork Boundary

This add-on intentionally focuses on what Blender's Python API can support without replacing core editors.

Reasonable in Python:

- N-panel based layer workflow
- Image import and material setup
- Property-driven layer metadata
- UIList-based management
- Key insertion and lightweight preset effects
- 2D camera setup and collection organization

Explicitly limited in this version:

- After Effects style bar timeline editor rendered as a native replacement
- Replacing Blender's Dope Sheet / Timeline editor behavior at the editor-framework level
- Full PSD-native non-destructive editing workflow
- Rich custom event-bar timeline interaction comparable to a forked application

If the project later moves toward a Blender fork or a standalone editor, the current `services`, `models`, and `properties` layout is meant to be reusable as the domain layer.
