"""Preset persistence utilities.

Educational Rationale:
Decouples file IO and schema envelope from UI logic. Enables future
migration strategies by version gating.
"""
from __future__ import annotations
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import SCHEMA_VERSION

PRESETS_FILENAME = "presets.json"

def get_presets_file() -> Path:
    base = Path.home() / ".auratyme"
    base.mkdir(parents=True, exist_ok=True)
    return base / PRESETS_FILENAME

def load_presets() -> Dict[str, Dict[str, Any]]:
    path = get_presets_file()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != SCHEMA_VERSION:
            return {}
        return data.get("presets", {})
    except Exception:
        return {}

def save_presets(presets: Dict[str, Dict[str, Any]]) -> None:
    payload = {"schema_version": SCHEMA_VERSION, "presets": presets}
    path = get_presets_file()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
