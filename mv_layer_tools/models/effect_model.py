from dataclasses import dataclass, field


@dataclass
class EffectModel:
    effect_name: str
    default_params: dict = field(default_factory=dict)
    required_channels: tuple[str, ...] = field(default_factory=tuple)
    can_stack: bool = True
