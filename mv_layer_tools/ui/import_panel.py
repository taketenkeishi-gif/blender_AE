from bpy.types import Panel

from ..constants import TAB_IMPORT
from .draw_helpers import draw_section_header
from .tabs import MVLT_PT_base_panel


class MVLT_PT_import_panel(MVLT_PT_base_panel, Panel):
    bl_idname = "MVLT_PT_import_panel"
    bl_label = "Import"
    bl_parent_id = "MVLT_PT_tabs"

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.scene.mvlt_ui_state.active_tab == TAB_IMPORT

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mvlt_import_settings

        intake = layout.box()
        draw_section_header(intake, "素材読込", icon="IMAGE_DATA")
        row = intake.row(align=True)
        row.scale_y = 1.15
        row.operator("mvlt.import_images", icon="IMAGE_DATA", text="静止画")
        row.operator("mvlt.import_sequence", icon="FILE_FOLDER", text="連番")

        placement = layout.box()
        draw_section_header(placement, "配置", icon="EMPTY_AXIS")
        placement.prop(settings, "place_mode", text="配置")
        placement.prop(settings, "z_offset_step", text="Z間隔")
        placement.prop(settings, "sort_mode", text="ソート")

        material = layout.box()
        draw_section_header(material, "描画", icon="MATERIAL")
        material.prop(settings, "align_center_on_camera", text="カメラ中央")
        material.prop(settings, "create_material_nodes", text="マテリアル生成")
        material.prop(settings, "image_alpha_mode", text="アルファ")
