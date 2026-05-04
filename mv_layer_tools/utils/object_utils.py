def is_mv_layer(obj):
    return getattr(obj, "mvlt_layer", None) and obj.mvlt_layer.is_mv_layer
