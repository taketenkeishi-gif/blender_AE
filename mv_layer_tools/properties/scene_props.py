from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup, Scene

from ..constants import MASTER_COLLECTION_NAME, SOURCE_KIND_IMAGE


class MVLT_SceneSettings(PropertyGroup):
    master_collection_name: StringProperty(name="Master Collection", default=MASTER_COLLECTION_NAME)
    auto_create_collections: BoolProperty(name="Auto Create Collections", default=True)
    default_layer_spacing: FloatProperty(name="Layer Spacing", default=0.1, min=0.0)
    default_frame_length: IntProperty(name="Default Frame Length", default=24, min=1)
    active_layer_index: IntProperty(name="Active Layer Index", default=-1)
    use_camera_facing_planes: BoolProperty(name="Camera Facing Planes", default=True)
    import_mode: EnumProperty(
        name="Import Mode",
        items=[(SOURCE_KIND_IMAGE, "Image", ""), ("SEQUENCE", "Sequence", "")],
        default=SOURCE_KIND_IMAGE,
    )
    default_opacity: FloatProperty(name="Default Opacity", default=1.0, min=0.0, max=1.0)
    default_category: StringProperty(name="Default Category", default="General")


def register():
    Scene.mvlt_scene_settings = PointerProperty(type=MVLT_SceneSettings)


def unregister():
    del Scene.mvlt_scene_settings
