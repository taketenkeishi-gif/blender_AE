# ファイルパス: bootstrap.py

import bpy

from .logging_utils import log_info
from .services.collection_service import ensure_master_collection


def initialize_addon():
    scene = getattr(bpy.context, "scene", None)
    if scene is not None:
        ensure_master_collection(scene)
    log_info("Addon initialized")


def shutdown_addon():
    try:
        from .viewport import shutdown_viewport_direct_edit

        shutdown_viewport_direct_edit()
    except Exception:
        pass
    try:
        from .services.external_api_server import stop_server

        stop_server()
    except Exception:
        pass
    log_info("Addon shutdown")
