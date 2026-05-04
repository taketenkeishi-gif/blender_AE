from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Object, PropertyGroup

from ..constants import LAYER_TYPE_IMAGE, SOURCE_KIND_IMAGE


class MVLT_LayerSettings(PropertyGroup):
    is_mv_layer: BoolProperty(name="Is MV Layer", default=False)
    layer_id: StringProperty(name="Layer ID")
    display_name: StringProperty(name="Display Name")
    layer_type: StringProperty(name="Layer Type", default=LAYER_TYPE_IMAGE)
    layer_order: IntProperty(name="Layer Order", default=0)
    group_name: StringProperty(name="Group Name")
    source_path: StringProperty(name="Source Path", subtype="FILE_PATH")
    source_kind: StringProperty(name="Source Kind", default=SOURCE_KIND_IMAGE)
    frame_start: IntProperty(name="Start", default=1)
    frame_end: IntProperty(name="End", default=24)
    opacity: FloatProperty(name="Opacity", default=1.0, min=0.0, max=1.0)
    is_locked: BoolProperty(name="Locked", default=False)
    is_hidden: BoolProperty(name="Hidden", default=False)
    is_selectable: BoolProperty(name="Selectable", default=True)
    notes: StringProperty(name="Notes")


def register():
    Object.mvlt_layer = PointerProperty(type=MVLT_LayerSettings)


def unregister():
    del Object.mvlt_layer
