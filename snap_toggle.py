from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from snap_media_toggle.config import load_config, write_default_config
from snap_media_toggle.detector import SnapDetector, SnapDetectorConfig
from snap_media_toggle.media_keys import toggle_media_play_pause


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = ROOT / "config.json"
DEFAULT_LOG_PATH = ROOT / "logs" / "snap-media-toggle.log"


def log(message: str, path: Path = DEFAULT_LOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    line = f"{stamp} {message}"
    print(line, flush=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def detector_config(config: dict[str, Any]) -> SnapDetectorConfig:
    return SnapDetectorConfig(
        cooldown_seconds=float(config["cooldown_seconds"]),
        min_peak=float(config["min_peak"]),
        threshold_multiplier=float(config["threshold_multiplier"]),
        min_crest_factor=float(config["min_crest_factor"]),
        max_active_fraction=float(config["max_active_fraction"]),
        noise_floor_alpha=float(config["noise_floor_alpha"]),
    )


def to_mono_samples(indata: Any) -> list[float]:
    if getattr(indata, "ndim", 1) == 1:
        return [float(value) for value in indata]
    return [float(row[0]) if len(row) == 1 else float(sum(row) / len(row)) for row in indata]


def stream_is_stale(last_callback_time: float, now: float, timeout_seconds: float) -> bool:
    return now - last_callback_time > timeout_seconds


def list_devices() -> int:
    import sounddevice as sd

    print(sd.query_devices())
    return 0


def listen(config_path: Path, dry_run: bool) -> int:
    import sounddevice as sd

    config = load_config(config_path)
    detector = SnapDetector(detector_config(config))
    last_callback_time = time.perf_counter()

    def callback(indata: Any, frames: int, time_info: Any, status: Any) -> None:
        nonlocal last_callback_time
        last_callback_time = time.perf_counter()
        if status:
            log(f"audio status: {status}")
        if not detector.process_block(to_mono_samples(indata), time.perf_counter()):
            return
        log("snap detected")
        if not dry_run:
            toggle_media_play_pause()

    log("listener starting" + (" in dry-run mode" if dry_run else ""))
    try:
        while True:
            last_callback_time = time.perf_counter()
            with sd.InputStream(
                device=config["device"],
                channels=int(config["channels"]),
                samplerate=int(config["sample_rate"]),
                blocksize=int(config["block_size"]),
                callback=callback,
            ):
                while True:
                    time.sleep(5)
                    if stream_is_stale(last_callback_time, time.perf_counter(), float(config["stream_timeout_seconds"])):
                        log("audio stream stale; restarting")
                        break
    except KeyboardInterrupt:
        log("listener stopped")
        return 0
    except Exception as exc:
        log(f"listener failed: {exc}")
        return 1

    return 0


def test_key() -> int:
    toggle_media_play_pause()
    log("sent media play/pause key")
    return 0


def init_config(config_path: Path) -> int:
    write_default_config(config_path)
    print(config_path)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Toggle media playback when a finger snap is detected.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("listen")
    subcommands.add_parser("dry-run")
    subcommands.add_parser("devices")
    subcommands.add_parser("test-key")
    subcommands.add_parser("init-config")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = args.command or "listen"
    if command == "devices":
        return list_devices()
    if command == "test-key":
        return test_key()
    if command == "init-config":
        return init_config(args.config)
    if command == "dry-run":
        return listen(args.config, dry_run=True)
    if command == "listen":
        return listen(args.config, dry_run=False)
    raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    sys.exit(main())
