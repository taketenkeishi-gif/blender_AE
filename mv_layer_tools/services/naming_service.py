from pathlib import Path


def display_name_from_path(path):
    return Path(path).stem


def make_layer_name(base_name, index=None):
    return f"{base_name}_{index:03d}" if index is not None else base_name
