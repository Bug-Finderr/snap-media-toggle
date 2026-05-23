from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SnapDetectorConfig:
    cooldown_seconds: float = 0.75
    min_peak: float = 0.25
    threshold_multiplier: float = 6.0
    min_crest_factor: float = 6.0
    max_active_fraction: float = 0.08
    noise_floor_alpha: float = 0.05


class SnapDetector:
    def __init__(self, config: SnapDetectorConfig) -> None:
        self.config = config
        self._noise_floor: float | None = None
        self._last_trigger_time = -1_000_000.0

    def process_block(self, samples: Sequence[float], now: float) -> bool:
        if not samples:
            return False

        peak = max(abs(float(sample)) for sample in samples)
        rms = math.sqrt(sum(float(sample) * float(sample) for sample in samples) / len(samples))
        crest_factor = peak / max(rms, 1e-9)

        if self._noise_floor is None:
            self._noise_floor = max(rms, 1e-9)

        threshold = max(self.config.min_peak, self._noise_floor * self.config.threshold_multiplier)
        active_cutoff = threshold * 0.35
        active_fraction = sum(1 for sample in samples if abs(float(sample)) >= active_cutoff) / len(samples)
        in_cooldown = now - self._last_trigger_time < self.config.cooldown_seconds
        triggered = (
            peak >= threshold
            and crest_factor >= self.config.min_crest_factor
            and active_fraction <= self.config.max_active_fraction
            and not in_cooldown
        )

        if triggered:
            self._last_trigger_time = now
        else:
            self._update_noise_floor(rms)

        return triggered

    def _update_noise_floor(self, rms: float) -> None:
        alpha = self.config.noise_floor_alpha
        current = self._noise_floor if self._noise_floor is not None else rms
        self._noise_floor = (current * (1.0 - alpha)) + (max(rms, 1e-9) * alpha)
