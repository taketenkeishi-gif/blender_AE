import os

from bpy.props import CollectionProperty, StringProperty
from bpy.types import Operator, OperatorFileListElement
from bpy_extras.io_utils import ImportHelper

from ..services.import_service import import_images


class MVLT_OT_import_images(Operator, ImportHelper):
    bl_idname = "mvlt.import_images"
    bl_label = "Import Images"
    bl_options = {"REGISTER", "UNDO"}

    filter_image: bool = True
    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        paths = [os.path.join(self.directory, file.name) for file in self.files]
        if not paths and self.filepath:
            paths = [self.filepath]
        imported = import_images(
            paths,
            context.scene.mvlt_scene_settings,
            context.scene.mvlt_import_settings,
            context.scene,
        )
        self.report({"INFO"}, f"Imported {len(imported)} image layers")
        return {"FINISHED"}
