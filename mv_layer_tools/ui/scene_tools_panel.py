from bpy.types import Panel

from ..constants import TAB_SCENE
from ..services.viewport_service import (
    get_active_mv_layer,
    get_direct_edit_feedback,
    is_direct_edit_mode_running,
)
from .draw_helpers import draw_section_header
from .tabs import MVLT_PT_base_panel


class MVLT_PT_scene_tools_panel(MVLT_PT_base_panel, Panel):
    bl_idname = "MVLT_PT_scene_tools_panel"
    bl_label = "Scene Tools"
    bl_parent_id = "MVLT_PT_tabs"

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.mvlt_ui_state.active_tab == TAB_SCENE

    def draw(self, context):
        layout = self.layout
        scene_settings = context.scene.mvlt_scene_settings

        tools = layout.box()
        draw_section_header(tools, "Scene Setup", icon="MODIFIER")
        row = tools.row(align=True)
        row.operator("mvlt.initialize_scene", icon="SCENE_DATA", text="Init 2D Scene")
        row.operator("mvlt.init_camera", icon="CAMERA_DATA", text="Init Camera")
        tools.operator("mvlt.refresh_layers", icon="FILE_REFRESH", text="Refresh Layers")

        direct_edit = layout.box()
        draw_section_header(direct_edit, "Direct Edit Mode", icon="ORIENTATION_VIEW")
        running = is_direct_edit_mode_running()
        state = "Running" if running else "Stopped"
        feedback = get_direct_edit_feedback()
        direct_edit.label(text=f"Status: {state}")

        active_obj = get_active_mv_layer(context)
        if active_obj is not None:
            direct_edit.label(text=f"Active: {active_obj.mvlt_layer.display_name or active_obj.name}")
        target = feedback.get("target", "")
        if target:
            direct_edit.label(text=f"Target: {target}")
        message = feedback.get("message", "")
        if message:
            direct_edit.label(text=f"Hint: {message}")

        row = direct_edit.row(align=True)
        row.operator("mvlt.start_direct_edit_mode", icon="PLAY", text="Start Direct Edit")
        row.operator("mvlt.stop_direct_edit_mode", icon="PAUSE", text="Stop Direct Edit")

        defaults = layout.box()
        draw_section_header(defaults, "Defaults", icon="PREFERENCES")
        defaults.prop(scene_settings, "master_collection_name", text="Master Collection")
        defaults.prop(scene_settings, "default_layer_spacing", text="Layer Spacing")
        defaults.prop(scene_settings, "default_frame_length", text="Default Length")
        defaults.prop(scene_settings, "default_category", text="Default Group")
        defaults.prop(scene_settings, "default_opacity", text="Default Opacity")
        defaults.prop(scene_settings, "use_camera_facing_planes", text="Camera Facing Planes")

        layout.prop(context.scene.mvlt_ui_state, "show_debug_info")
        if context.scene.mvlt_ui_state.show_debug_info:
            debug = layout.box()
            debug.label(text=f"Scene frame: {context.scene.frame_current}")
            debug.label(text=f"Layer items: {len(context.scene.mvlt_ui_state.layer_items)}")
            debug.label(text=f"Direct edit: {state}")
            debug.label(text=f"Direct state: {feedback.get('state', '')}")