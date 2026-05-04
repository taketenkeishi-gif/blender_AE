def ensure_action(obj):
    if obj.animation_data is None:
        obj.animation_data_create()
    return obj.animation_data.action
