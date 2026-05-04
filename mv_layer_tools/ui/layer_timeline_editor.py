from bpy.types import Panel

from ..services.selection_service import get_active_layer_object, refresh_layer_ui_items


class MVLT_PT_layer_timeline_editor(Panel):
    bl_idname = "MVLT_PT_layer_timeline_editor"
    bl_label = "Layer Timeline Editor"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "AVIUTL"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ui_state = scene.mvlt_ui_state

        if len(ui_state.layer_items) == 0 and any(getattr(obj, "mvlt_layer", None) and obj.mvlt_layer.is_mv_layer for obj in scene.objects):
            refresh_layer_ui_items(scene)

        head = layout.box()
        title = head.row(align=True)
        title.label(text="Layer / Timeline", icon="SEQ_STRIP_DUPLICATE")
        title.label(text=f"Frame {scene.frame_current}")
        head.prop(ui_state, "layer_filter_text", text="", icon="VIEWZOOM")
        head.template_list("MVLT_UL_layer_list", "", ui_state, "layer_items", ui_state, "layer_list_index", rows=10)

        tools = head.row(align=True)
        tools.operator("mvlt.refresh_layers", text="", icon="FILE_REFRESH")
        tools.operator("mvlt.register_selected_as_layer", text="", icon="ADD")
        tools.operator("mvlt.delete_layer", text="", icon="TRASH")
        tools.operator("mvlt.duplicate_layer", text="", icon="DUPLICATE")
        up = tools.operator("mvlt.reorder_layer", text="", icon="TRIA_UP")
        up.direction = -1
        down = tools.operator("mvlt.reorder_layer", text="", icon="TRIA_DOWN")
        down.direction = 1

        obj = get_active_layer_object(context)
        details = layout.box()
        if obj is None:
            details.label(text="No active layer. Select a layer from the list.", icon="INFO")
            return

        summary = details.row(align=True)
        summary.label(text=obj.mvlt_layer.display_name or obj.name, icon="IMAGE_DATA")
        summary.label(text=obj.mvlt_layer.group_name or "-", icon="FILE_PARENT")
        summary.label(text=obj.mvlt_layer.layer_type)

        switches = details.row(align=True)
        switches.operator("mvlt.toggle_visibility", text="Visible", icon="HIDE_OFF")
        switches.operator("mvlt.toggle_lock", text="Lock", icon="LOCKED")
        switches.prop(obj.mvlt_layer, "opacity", text="Opacity", slider=True)

        timeline = details.box()
        timeline.label(text="Timeline", icon="TIME")
        move = timeline.row(align=True)
        left5 = move.operator("mvlt.nudge_frame", text="-5")
        left5.delta = -5
        left1 = move.operator("mvlt.nudge_frame", text="-1")
        left1.delta = -1
        move.label(text=f"Current {scene.frame_current}")
        right1 = move.operator("mvlt.nudge_frame", text="+1")
        right1.delta = 1
        right5 = move.operator("mvlt.nudge_frame", text="+5")
        right5.delta = 5

        io = timeline.row(align=True)
        io.prop(obj.mvlt_layer, "frame_start", text="In")
        io.prop(obj.mvlt_layer, "frame_end", text="Out")

        marks = timeline.row(align=True)
        marks.operator("mvlt.set_layer_in_from_current", text="Current -> In")
        marks.operator("mvlt.set_layer_out_from_current", text="Current -> Out")

        jumps = timeline.row(align=True)
        jumps.operator("mvlt.jump_to_layer_start", text="Jump In")
        jumps.operator("mvlt.jump_to_layer_end", text="Jump Out")

        keys = timeline.row(align=True)
        keys.operator("mvlt.add_primary_keys", text="Primary Keys", icon="KEY_HLT")
        keys.operator("mvlt.add_transform_keys", text="Transform")
        keys.operator("mvlt.add_opacity_key", text="Opacity")

        effects = details.box()
        effects.label(text="Quick Effects", icon="SHADERFX")
        fade = effects.row(align=True)
        fade.operator("mvlt.apply_fade_in", text="Fade In")
        fade.operator("mvlt.apply_fade_out", text="Fade Out")
        motion = effects.row(align=True)
        motion.operator("mvlt.apply_shake", text="Shake")
        motion.operator("mvlt.apply_zoom", text="Zoom")
