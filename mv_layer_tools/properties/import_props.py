from bpy.props import BoolProperty, EnumProperty, FloatProperty, PointerProperty
from bpy.types import PropertyGroup, Scene


class MVLT_ImportSettings(PropertyGroup):
    place_mode: EnumProperty(
        name="Placement",
        items=[("STACK_Z", "Stack Z", ""), ("LINE_X", "Line X", "")],
        default="STACK_Z",
    )
    z_offset_step: FloatProperty(name="Z Step", default=0.1, min=0.0)
    sort_mode: EnumProperty(
        name="Sort",
        items=[("NAME", "Name", ""), ("FILE", "File Order", "")],
        default="FILE",
    )
    align_center_on_camera: BoolProperty(name="Center On Camera", default=True)
    create_material_nodes: BoolProperty(name="Create Material", default=True)
    image_alpha_mode: EnumProperty(
        name="Alpha",
        items=[("BLEND", "Blend", ""), ("CLIP", "Clip", "")],
        default="BLEND",
    )


def register():
    Scene.mvlt_import_settings = PointerProperty(type=MVLT_ImportSettings)


def unregister():
    del Scene.mvlt_import_settings
