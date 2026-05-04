from bpy.types import Panel

from ..constants import TAB_LAYERS
from .draw_helpers import draw_active_layer_header, draw_section_header
from .tabs import MVLT_PT_base_panel


class MVLT_PT_layers_panel(MVLT_PT_base_panel, Panel):
    bl_idname = "MVLT_PT_layers_panel"
    bl_label = "Layers"
    bl_parent_id = "MVLT_PT_tabs"

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.mvlt_ui_state.active_tab == TAB_LAYERS

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ui_state = scene.mvlt_ui_state

        top = layout.box()
        header = top.row(align=True)
        header.label(text="レイヤー一覧", icon="SEQ_STRIP_DUPLICATE")
        header.label(text=f"{len(ui_state.layer_items)} 件")
        top.prop(ui_state, "layer_filter_text", text="", icon="VIEWZOOM")
        top.template_list("MVLT_UL_layer_list", "", ui_state, "layer_items", ui_state, "layer_list_index", rows=9)

        controls = top.row(align=True)
        controls.operator("mvlt.refresh_layers", icon="FILE_REFRESH", text="")
        controls.operator("mvlt.register_selected_as_layer", icon="ADD", text="")
        controls.operator("mvlt.delete_layer", icon="TRASH", text="")
        controls.operator("mvlt.duplicate_layer", icon="DUPLICATE", text="")

        order_row = top.row(align=True)
        up = order_row.operator("mvlt.reorder_layer", text="Move Up")
        up.direction = -1
        down = order_row.operator("mvlt.reorder_layer", text="Move Down")
        down.direction = 1

        obj = draw_active_layer_header(layout, context)
        if obj is None:
            return

        identity = layout.box()
        draw_section_header(identity, "選択レイヤー", icon="OUTLINER_OB_IMAGE")
        name_row = identity.row(align=True)
        name_row.prop(obj.mvlt_layer, "display_name", text="名前")
        name_row.prop(obj.mvlt_layer, "group_name", text="グループ")
        identity.prop(obj.mvlt_layer, "notes", text="メモ")

        toggles = layout.box()
        draw_section_header(toggles, "スイッチ", icon="OPTIONS")
        switch_row = toggles.row(align=True)
        switch_row.scale_y = 1.05
        switch_row.operator("mvlt.toggle_visibility", icon="HIDE_OFF", text="表示")
        switch_row.operator("mvlt.toggle_lock", icon="LOCKED", text="ロック")

        info = layout.box()
        draw_section_header(info, "素材 / 尺", icon="FILE")
        info.label(text=f"Source: {obj.mvlt_layer.source_path or '-'}")
        info.label(text=f"In/Out: {obj.mvlt_layer.frame_start} - {obj.mvlt_layer.frame_end}")
