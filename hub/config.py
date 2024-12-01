from dataclasses import dataclass

@dataclass
class Config:
    repository: str
    repositoy_path: str

    files_to_track: list[str]
