from .animation_service import insert_opacity_key, insert_transform_keys


def set_opacity(obj, value):
    obj["mvlt_opacity"] = value
    obj.mvlt_layer.opacity = value
    for slot in obj.material_slots:
        material = slot.material
        if material and material.use_nodes:
            principled = next((n for n in material.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
            if principled:
                principled.inputs["Alpha"].default_value = value


def apply_fade_in(obj, start_frame, duration):
    target = obj.mvlt_layer.opacity or 1.0
    set_opacity(obj, 0.0)
    insert_opacity_key(obj, start_frame)
    set_opacity(obj, target)
    insert_opacity_key(obj, start_frame + int(duration))


def apply_fade_out(obj, end_frame, duration):
    current = obj.mvlt_layer.opacity or 1.0
    set_opacity(obj, current)
    insert_opacity_key(obj, end_frame - int(duration))
    set_opacity(obj, 0.0)
    insert_opacity_key(obj, end_frame)


def apply_shake(obj, start_frame, end_frame, strength, speed):
    base_location = obj.location.copy()
    interval = max(1, int(6 / max(speed, 0.1)))
    direction = 1.0
    for frame in range(start_frame, end_frame + 1, interval):
        obj.location.x = base_location.x + (strength * direction)
        obj.location.y = base_location.y + (strength * 0.35 * -direction)
        insert_transform_keys(obj, frame)
        direction *= -1.0
    obj.location = base_location
    insert_transform_keys(obj, end_frame)


def apply_zoom(obj, start_frame, end_frame, amount):
    base_scale = obj.scale.copy()
    obj.scale = base_scale
    insert_transform_keys(obj, start_frame)
    obj.scale = (base_scale.x * (1.0 + amount), base_scale.y * (1.0 + amount), base_scale.z)
    insert_transform_keys(obj, end_frame)
    obj.scale = base_scale
