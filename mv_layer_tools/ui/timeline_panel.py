from bpy.types import Panel

from ..constants import TAB_TIMELINE
from .draw_helpers import draw_active_layer_header, draw_section_header
from .tabs import MVLT_PT_base_panel


class MVLT_PT_timeline_panel(MVLT_PT_base_panel, Panel):
    bl_idname = "MVLT_PT_timeline_panel"
    bl_label = "Timeline"
    bl_parent_id = "MVLT_PT_tabs"

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.mvlt_ui_state.active_tab == TAB_TIMELINE

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = draw_active_layer_header(layout, context)
        if obj is None:
            return

        timing = layout.box()
        draw_section_header(timing, "時間設定", icon="TIME")
        head = timing.row(align=True)
        head.label(text=f"現在フレーム {scene.frame_current}")
        left5 = head.operator("mvlt.nudge_frame", text="-5")
        left5.delta = -5
        left1 = head.operator("mvlt.nudge_frame", text="-1")
        left1.delta = -1
        right1 = head.operator("mvlt.nudge_frame", text="+1")
        right1.delta = 1
        right5 = head.operator("mvlt.nudge_frame", text="+5")
        right5.delta = 5

        io_row = timing.row(align=True)
        io_row.prop(obj.mvlt_layer, "frame_start", text="In")
        io_row.prop(obj.mvlt_layer, "frame_end", text="Out")

        nav = timing.row(align=True)
        nav.operator("mvlt.jump_to_layer_start", text="先頭へ")
        nav.operator("mvlt.jump_to_layer_end", text="末尾へ")

        mark = timing.row(align=True)
        mark.operator("mvlt.set_layer_in_from_current", text="現在をIn")
        mark.operator("mvlt.set_layer_out_from_current", text="現在をOut")
        timing.label(text=f"[{obj.mvlt_layer.frame_start:>4}] {context.scene.mvlt_ui_state.layer_items[context.scene.mvlt_ui_state.layer_list_index].timeline_bar if context.scene.mvlt_ui_state.layer_list_index >= 0 and context.scene.mvlt_ui_state.layer_list_index < len(context.scene.mvlt_ui_state.layer_items) else ''} [{obj.mvlt_layer.frame_end:>4}]")

        keys = layout.box()
        draw_section_header(keys, "キー操作", icon="KEY_HLT")
        keys.operator("mvlt.add_primary_keys", icon="KEY_HLT", text="主要キーを打つ")
        shortcuts = keys.row(align=True)
        shortcuts.operator("mvlt.add_transform_keys", text="移動/回転/拡大")
        shortcuts.operator("mvlt.add_opacity_key", text="不透明度")
