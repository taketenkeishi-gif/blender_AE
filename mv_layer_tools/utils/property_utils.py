def frame_summary(layer):
    return f"{layer.frame_start}-{layer.frame_end}"


def timeline_bar(scene, layer, width=16):
    scene_start = scene.frame_start
    scene_end = max(scene.frame_end, scene_start + 1)
    current = scene.frame_current

    start_ratio = (layer.frame_start - scene_start) / (scene_end - scene_start)
    end_ratio = (layer.frame_end - scene_start) / (scene_end - scene_start)
    current_ratio = (current - scene_start) / (scene_end - scene_start)

    start_idx = max(0, min(width - 1, int(start_ratio * width)))
    end_idx = max(start_idx, min(width - 1, int(end_ratio * width)))
    current_idx = max(0, min(width - 1, int(current_ratio * width)))

    cells = []
    for idx in range(width):
        char = "-"
        if start_idx <= idx <= end_idx:
            char = "="
        if idx == current_idx:
            char = "|"
        cells.append(char)
    return "".join(cells)
