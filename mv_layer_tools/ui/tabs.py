from bpy.types import Panel

from ..constants import PANEL_CATEGORY


class MVLT_PT_base_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = PANEL_CATEGORY

    @classmethod
    def poll(cls, context):
        return context.scene is not None


class MVLT_PT_tabs(MVLT_PT_base_panel):
    bl_idname = "MVLT_PT_tabs"
    bl_label = "AviUtl Mode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ui_state = scene.mvlt_ui_state

        header = layout.box()
        title = header.row(align=True)
        title.label(text="編集ウィンドウ", icon="NODE_COMPOSITING")
        title.label(text=f"{len(ui_state.layer_items)} Layer")

        header.prop(ui_state, "active_tab", expand=True)
        status = header.row(align=True)
        status.label(text=f"F {scene.frame_current}")
        status.label(text=f"Scene {scene.frame_start}-{scene.frame_end}")
