from ..services.selection_service import get_active_layer_object


def draw_section_header(layout, title, icon="BLANK1"):
    row = layout.row(align=True)
    row.label(text=title, icon=icon)
    return row


def draw_active_layer_header(layout, context):
    obj = get_active_layer_object(context)
    box = layout.box()
    if obj is None:
        box.label(text="No active MV layer", icon="INFO")
        return None
    top = box.row(align=True)
    top.label(text=obj.mvlt_layer.display_name or obj.name, icon="IMAGE_DATA")
    top.label(text=obj.mvlt_layer.layer_type, icon="DOT")

    meta = box.row(align=True)
    meta.label(text=f"In {obj.mvlt_layer.frame_start}")
    meta.label(text=f"Out {obj.mvlt_layer.frame_end}")
    meta.label(text=f"Grp {obj.mvlt_layer.group_name or '-'}")
    return obj
