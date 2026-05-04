from dataclasses import dataclass


@dataclass
class ImportModel:
    path: str
    source_kind: str
    display_name: str
