from bpy.props import FloatProperty, PointerProperty
from bpy.types import PropertyGroup, Scene


class MVLT_EffectSettings(PropertyGroup):
    fade_default_duration: FloatProperty(name="Fade Duration", default=12.0, min=1.0)
    shake_default_strength: FloatProperty(name="Shake Strength", default=0.08, min=0.0)
    shake_default_speed: FloatProperty(name="Shake Speed", default=1.0, min=0.1)
    zoom_default_amount: FloatProperty(name="Zoom Amount", default=0.15, min=0.0)
    color_boost_default: FloatProperty(name="Color Boost", default=1.0, min=0.0)


def register():
    Scene.mvlt_effect_settings = PointerProperty(type=MVLT_EffectSettings)


def unregister():
    del Scene.mvlt_effect_settings
