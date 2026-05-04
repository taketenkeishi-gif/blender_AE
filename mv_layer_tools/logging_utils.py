from .constants import ADDON_PREFIX


def log_info(message):
    print(f"[{ADDON_PREFIX}] {message}")


def log_error(message):
    print(f"[{ADDON_PREFIX}][ERROR] {message}")
