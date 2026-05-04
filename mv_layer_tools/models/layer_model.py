from dataclasses import dataclass


@dataclass
class LayerModel:
    identifier: str
    display_name: str
    layer_type: str
    frame_start: int
    frame_end: int
    is_hidden: bool
    group_name: str
    source_path: str
