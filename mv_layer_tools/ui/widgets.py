def draw_operator_row(layout, left_id, right_id, left_text="", right_text=""):
    row = layout.row(align=True)
    row.operator(left_id, text=left_text)
    row.operator(right_id, text=right_text)
