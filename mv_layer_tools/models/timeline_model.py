from dataclasses import dataclass, field


@dataclass
class TimelineModel:
    frame_start: int
    frame_end: int
    keyable_channels: tuple[str, ...] = field(default_factory=tuple)
    current_frame_relation: str = "INSIDE"
