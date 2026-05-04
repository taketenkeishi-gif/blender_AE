from pathlib import Path

from bpy.props import StringProperty
from bpy.types import Operator

from ..services.import_service import import_images


class MVLT_OT_import_sequence(Operator):
    bl_idname = "mvlt.import_sequence"
    bl_label = "Import Sequence Folder"
    bl_options = {"REGISTER", "UNDO"}

    directory: StringProperty(name="Directory", subtype="DIR_PATH")

    def execute(self, context):
        directory = Path(self.directory)
        if not directory.exists():
            self.report({"ERROR"}, "Directory not found")
            return {"CANCELLED"}
        image_paths = [str(path) for path in sorted(directory.iterdir()) if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
        if not image_paths:
            self.report({"ERROR"}, "No images found in directory")
            return {"CANCELLED"}
        imported = import_images(
            [image_paths[0]],
            context.scene.mvlt_scene_settings,
            context.scene.mvlt_import_settings,
            context.scene,
        )
        obj = imported[0]
        obj.mvlt_layer.source_kind = "SEQUENCE"
        obj.mvlt_layer.source_path = str(directory)
        self.report({"INFO"}, f"Registered sequence source from {directory.name}")
        return {"FINISHED"}
