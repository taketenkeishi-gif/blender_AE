from bpy.props import BoolProperty, CollectionProperty, EnumProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup, Scene

from ..constants import TAB_EFFECTS, TAB_IMPORT, TAB_LAYERS, TAB_SCENE, TAB_TIMELINE


def _refresh_layer_filter(self, context):
    if context is None or context.scene is None:
        return
    from ..services.selection_service import refresh_layer_ui_items

    refresh_layer_ui_items(context.scene)


class MVLT_LayerListItem(PropertyGroup):
    object_name: StringProperty(name="Object Name")
    display_name: StringProperty(name="Display Name")
    layer_type: StringProperty(name="Layer Type")
    frame_summary: StringProperty(name="Frames")
    group_name: StringProperty(name="Group")
    timeline_bar: StringProperty(name="Timeline Bar")
    is_hidden: BoolProperty(name="Hidden", default=False)
    is_locked: BoolProperty(name="Locked", default=False)


class MVLT_UIState(PropertyGroup):
    active_tab: EnumProperty(
        name="Tab",
        items=[
            (TAB_IMPORT, "Imp", "Import and footage intake", "IMPORT", 0),
            (TAB_LAYERS, "Lay", "Layer stack and management", "SEQ_LUMA_WAVEFORM", 1),
            (TAB_TIMELINE, "Time", "Timing and keyframes", "TIME", 2),
            (TAB_EFFECTS, "FX", "Frequent animation effects", "SHADERFX", 3),
            (TAB_SCENE, "Scene", "Scene and camera tools", "SCENE_DATA", 4),
        ],
        default=TAB_IMPORT,
    )
    selected_effect_preset: StringProperty(name="Selected Preset", default="Default")
    layer_filter_text: StringProperty(name="Filter", update=_refresh_layer_filter)
    show_advanced_controls: BoolProperty(name="Advanced", default=False)
    show_debug_info: BoolProperty(name="Debug", default=False)
    layer_items: CollectionProperty(type=MVLT_LayerListItem)
    layer_list_index: IntProperty(name="Layer Index", default=-1)


def register():
    Scene.mvlt_ui_state = PointerProperty(type=MVLT_UIState)


def unregister():
    del Scene.mvlt_ui_state
