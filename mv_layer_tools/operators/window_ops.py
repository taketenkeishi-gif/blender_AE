from bpy.types import Menu, Operator

from ..constants import TAB_TIMELINE

from ..services.selection_service import get_active_layer_object
from ..services.selection_service import refresh_layer_ui_items


def _draw_active_header(layout, context):
    obj = get_active_layer_object(context)
    box = layout.box()
    if obj is None:
        box.label(text="No active layer", icon="INFO")
        return None
    row = box.row(align=True)
    row.label(text=obj.mvlt_layer.display_name or obj.name, icon="IMAGE_DATA")
    row.label(text=f"In {obj.mvlt_layer.frame_start}")
    row.label(text=f"Out {obj.mvlt_layer.frame_end}")
    return obj


class MVLT_OT_popup_base(Operator):
    bl_options = {"INTERNAL"}
    popup_title = "MVLT"
    popup_icon = "WINDOW"
    popup_width = 420

    def _popup_draw(self, popup, context):
        self.draw_contents(popup.layout, context)

    def execute(self, context):
        context.window_manager.popup_menu(self._popup_draw, title=self.popup_title, icon=self.popup_icon)
        return {"FINISHED"}

    def invoke(self, context, _event):
        return context.window_manager.invoke_popup(self, width=self.popup_width)

    def draw(self, context):
        self.draw_contents(self.layout, context)

    def draw_contents(self, layout, context):
        layout.label(text="Not implemented")


class MVLT_OT_open_import_window(MVLT_OT_popup_base):
    bl_idname = "mvlt.open_import_window"
    bl_label = "Open Import Window"
    popup_title = "Material Import"
    popup_icon = "IMAGE_DATA"
    popup_width = 420

    def draw_contents(self, layout, context):
        settings = context.scene.mvlt_import_settings
        layout.label(text="Material Intake", icon="IMAGE_DATA")
        row = layout.row(align=True)
        row.operator("mvlt.import_images", text="Import Stills", icon="IMAGE_DATA")
        row.operator("mvlt.import_sequence", text="Import Sequence", icon="FILE_FOLDER")
        layout.separator()
        layout.prop(settings, "place_mode", text="Placement")
        layout.prop(settings, "z_offset_step", text="Z Step")
        layout.prop(settings, "sort_mode", text="Sort")
        layout.prop(settings, "align_center_on_camera", text="Center On Camera")
        layout.prop(settings, "create_material_nodes", text="Build Material")
        layout.prop(settings, "image_alpha_mode", text="Alpha")


class MVLT_OT_open_layers_window(MVLT_OT_popup_base):
    bl_idname = "mvlt.open_layers_window"
    bl_label = "Open Layers Window"
    popup_title = "Layer Window"
    popup_icon = "SEQ_STRIP_DUPLICATE"
    popup_width = 520

    def draw_contents(self, layout, context):
        scene = context.scene
        ui_state = scene.mvlt_ui_state
        layout.label(text="Layer Stack", icon="SEQ_STRIP_DUPLICATE")
        layout.prop(ui_state, "layer_filter_text", text="", icon="VIEWZOOM")
        layout.template_list("MVLT_UL_layer_list", "", ui_state, "layer_items", ui_state, "layer_list_index", rows=10)

        row = layout.row(align=True)
        row.operator("mvlt.refresh_layers", text="", icon="FILE_REFRESH")
        row.operator("mvlt.register_selected_as_layer", text="", icon="ADD")
        row.operator("mvlt.delete_layer", text="", icon="TRASH")
        row.operator("mvlt.duplicate_layer", text="", icon="DUPLICATE")

        row = layout.row(align=True)
        up = row.operator("mvlt.reorder_layer", text="Up")
        up.direction = -1
        down = row.operator("mvlt.reorder_layer", text="Down")
        down.direction = 1

        obj = _draw_active_header(layout, context)
        if obj is None:
            return

        layout.prop(obj.mvlt_layer, "display_name", text="Name")
        layout.prop(obj.mvlt_layer, "group_name", text="Group")
        layout.prop(obj.mvlt_layer, "notes", text="Notes")

        row = layout.row(align=True)
        row.operator("mvlt.toggle_visibility", text="Visible", icon="HIDE_OFF")
        row.operator("mvlt.toggle_lock", text="Lock", icon="LOCKED")


class MVLT_OT_open_timeline_window(MVLT_OT_popup_base):
    bl_idname = "mvlt.open_timeline_window"
    bl_label = "Open Timeline Window"
    popup_title = "Timeline Window"
    popup_icon = "TIME"
    popup_width = 460

    def draw_contents(self, layout, context):
        obj = _draw_active_header(layout, context)
        if obj is None:
            return

        scene = context.scene
        head = layout.row(align=True)
        head.label(text=f"Current {scene.frame_current}", icon="TIME")
        left5 = head.operator("mvlt.nudge_frame", text="-5")
        left5.delta = -5
        left1 = head.operator("mvlt.nudge_frame", text="-1")
        left1.delta = -1
        right1 = head.operator("mvlt.nudge_frame", text="+1")
        right1.delta = 1
        right5 = head.operator("mvlt.nudge_frame", text="+5")
        right5.delta = 5

        row = layout.row(align=True)
        row.prop(obj.mvlt_layer, "frame_start", text="In")
        row.prop(obj.mvlt_layer, "frame_end", text="Out")

        row = layout.row(align=True)
        row.operator("mvlt.jump_to_layer_start", text="Jump In")
        row.operator("mvlt.jump_to_layer_end", text="Jump Out")

        row = layout.row(align=True)
        row.operator("mvlt.set_layer_in_from_current", text="Current -> In")
        row.operator("mvlt.set_layer_out_from_current", text="Current -> Out")

        layout.separator()
        layout.operator("mvlt.add_primary_keys", text="Add Primary Keys", icon="KEY_HLT")
        row = layout.row(align=True)
        row.operator("mvlt.add_transform_keys", text="Transform")
        row.operator("mvlt.add_opacity_key", text="Opacity")


class MVLT_OT_open_effects_window(MVLT_OT_popup_base):
    bl_idname = "mvlt.open_effects_window"
    bl_label = "Open Effects Window"
    popup_title = "Effects Window"
    popup_icon = "SHADERFX"
    popup_width = 420

    def draw_contents(self, layout, context):
        obj = _draw_active_header(layout, context)
        if obj is None:
            return

        settings = context.scene.mvlt_effect_settings
        layout.prop(obj.mvlt_layer, "opacity", text="Opacity", slider=True)
        apply_op = layout.operator("mvlt.set_opacity", text="Apply Opacity", icon="NODE_MATERIAL")
        apply_op.value = obj.mvlt_layer.opacity

        layout.separator()
        layout.prop(settings, "fade_default_duration", text="Fade Length")
        row = layout.row(align=True)
        row.operator("mvlt.apply_fade_in", text="Fade In")
        row.operator("mvlt.apply_fade_out", text="Fade Out")

        layout.separator()
        layout.prop(settings, "shake_default_strength", text="Shake Strength")
        layout.prop(settings, "shake_default_speed", text="Shake Speed")
        layout.operator("mvlt.apply_shake", text="Apply Shake", icon="DRIVER")

        layout.separator()
        layout.prop(settings, "zoom_default_amount", text="Zoom Amount")
        layout.operator("mvlt.apply_zoom", text="Apply Zoom", icon="VIEWZOOM")


class MVLT_OT_open_scene_window(MVLT_OT_popup_base):
    bl_idname = "mvlt.open_scene_window"
    bl_label = "Open Scene Window"
    popup_title = "Scene Window"
    popup_icon = "PREFERENCES"
    popup_width = 420

    def draw_contents(self, layout, context):
        scene_settings = context.scene.mvlt_scene_settings
        layout.label(text="Setup / Defaults", icon="MODIFIER")

        row = layout.row(align=True)
        row.operator("mvlt.initialize_scene", text="Init 2D Scene", icon="SCENE_DATA")
        row.operator("mvlt.init_camera", text="Init Camera", icon="CAMERA_DATA")
        layout.operator("mvlt.refresh_layers", text="Refresh Layer List", icon="FILE_REFRESH")

        layout.separator()
        layout.prop(scene_settings, "master_collection_name", text="Master Collection")
        layout.prop(scene_settings, "default_layer_spacing", text="Layer Spacing")
        layout.prop(scene_settings, "default_frame_length", text="Default Length")
        layout.prop(scene_settings, "default_category", text="Default Group")
        layout.prop(scene_settings, "default_opacity", text="Default Opacity")
        layout.prop(scene_settings, "use_camera_facing_planes", text="Camera Facing")


class MVLT_OT_open_layer_timeline_editor(Operator):
    bl_idname = "mvlt.open_layer_timeline_editor"
    bl_label = "Open Timeline Tab"

    def execute(self, context):
        refresh_layer_ui_items(context.scene)
        context.scene.mvlt_ui_state.active_tab = TAB_TIMELINE
        if context.area is not None:
            context.area.tag_redraw()
        self.report({"INFO"}, "Opened the MVLT Timeline tab")
        return {"FINISHED"}

class MVLT_MT_topbar_menu(Menu):
    bl_idname = "MVLT_MT_topbar_menu"
    bl_label = "AviUtl"

    def draw(self, _context):
        layout = self.layout
        layout.operator("mvlt.open_import_window", text="Material Window", icon="IMAGE_DATA")
        layout.operator("mvlt.open_layer_timeline_editor", text="Timeline Tab", icon="TIME")
        layout.operator("mvlt.open_effects_window", text="Effects Window", icon="SHADERFX")
        layout.operator("mvlt.open_scene_window", text="Scene Window", icon="PREFERENCES")

