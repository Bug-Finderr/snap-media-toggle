from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "sample_rate": 44100,
    "block_size": 1024,
    "channels": 1,
    "cooldown_seconds": 0.75,
    "min_peak": 0.25,
    "threshold_multiplier": 6.0,
    "min_crest_factor": 6.0,
    "max_active_fraction": 0.08,
    "noise_floor_alpha": 0.05,
    "device": None,
}


def load_config(path: str | Path) -> dict[str, Any]:
    config = DEFAULT_CONFIG.copy()
    path = Path(path)
    if not path.exists():
        return config

    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Config must be a JSON object: {path}")

    for key in DEFAULT_CONFIG:
        if key in loaded:
            config[key] = loaded[key]
    return config


def write_default_config(path: str | Path) -> None:
    path = Path(path)
    if path.exists():
        return
    path.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
