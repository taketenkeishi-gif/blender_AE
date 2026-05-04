from bpy.types import Panel

from ..constants import TAB_EFFECTS
from .draw_helpers import draw_active_layer_header, draw_section_header
from .tabs import MVLT_PT_base_panel


class MVLT_PT_effects_panel(MVLT_PT_base_panel, Panel):
    bl_idname = "MVLT_PT_effects_panel"
    bl_label = "Effects"
    bl_parent_id = "MVLT_PT_tabs"

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.mvlt_ui_state.active_tab == TAB_EFFECTS

    def draw(self, context):
        layout = self.layout
        obj = draw_active_layer_header(layout, context)
        if obj is None:
            return

        effect_settings = context.scene.mvlt_effect_settings
        blend = layout.box()
        draw_section_header(blend, "基本", icon="NODE_MATERIAL")
        blend.prop(obj.mvlt_layer, "opacity", text="不透明度", slider=True)
        apply_row = blend.row(align=True)
        set_op = apply_row.operator("mvlt.set_opacity", text="数値を反映")
        set_op.value = obj.mvlt_layer.opacity

        fade_box = layout.box()
        draw_section_header(fade_box, "フェード", icon="IPO_EASE_IN_OUT")
        fade_box.prop(effect_settings, "fade_default_duration", text="長さ")
        fade_row = fade_box.row(align=True)
        fade_row.operator("mvlt.apply_fade_in", text="イン")
        fade_row.operator("mvlt.apply_fade_out", text="アウト")

        shake_box = layout.box()
        draw_section_header(shake_box, "振動", icon="DRIVER")
        shake_box.prop(effect_settings, "shake_default_strength", text="強さ")
        shake_box.prop(effect_settings, "shake_default_speed", text="速さ")
        shake_box.operator("mvlt.apply_shake", text="振動を適用")

        zoom_box = layout.box()
        draw_section_header(zoom_box, "ズーム", icon="VIEWZOOM")
        zoom_box.prop(effect_settings, "zoom_default_amount", text="量")
        zoom_box.operator("mvlt.apply_zoom", text="ズームを適用")
