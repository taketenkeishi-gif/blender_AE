def require_object(obj, message="No active object"):
    if obj is None:
        raise ValueError(message)
    return obj
