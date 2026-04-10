import os
from pathlib import Path

def setup_directories(settings: dict):
    dirs = settings.get("directories", {})
    for d in dirs.values():
        path = Path(d)
        path.mkdir(parents=True, exist_ok=True)
        
def get_project_root() -> Path:
    return Path(__file__).parent.parent
