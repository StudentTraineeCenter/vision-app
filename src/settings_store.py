import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"

DEFAULTS = {
    "export_dir": None,
    "default_format": "JPEG",
    "default_quality": 85, 
    "accent": "a78bfa",
    "recents": [],
}

def load_settings() -> dict:
    settings = dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings.update(json.load(f))
    except (OSError, ValueError):
        pass
    return settings

def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

from datetime import date
MAX_RECENTS = 8

def add_recent(settings: dict, path: str) -> None:
    items = [r for r in settings.get("recents", []) if r["path"] != path]
    items.insert(0, {"path": path, "opened": date.today().strftime("%d.%m.%Y")})
    settings["recents"] = items[:MAX_RECENTS]
    save_settings(settings)

def get_recents(settings: dict) -> list:
    from pathlib import Path
    return [r for r in settings.get("recents", []) if Path(r["path"]).exists()]