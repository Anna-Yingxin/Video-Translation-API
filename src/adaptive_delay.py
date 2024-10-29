MIN_DELAY_SEC = 2.0
MAX_DELAY_SEC = 10.0

# Percentage thresholds
EARLY_PHASE_END = 70.0
MID_PHASE_END = 90.0


class DelayStrategies:
    def __init__(
        self,
        estimate_translation_time_sec,
    ):
        self.estimate_translation_time_sec = estimate_translation_time_sec

    def adaptive_delay(self, elapsed_time_sec: float) -> float:
        progress = min(
            100.0, (elapsed_time_sec / self.estimate_translation_time_sec) * 100
        )

        if progress < EARLY_PHASE_END:
            delay = MAX_DELAY_SEC * (1 - progress / EARLY_PHASE_END)
        elif progress < MID_PHASE_END:
            mid_progress = (progress - EARLY_PHASE_END) / (
                MID_PHASE_END - EARLY_PHASE_END
            )
            delay = MAX_DELAY_SEC * 0.5 * (1 - mid_progress)
        else:
            delay = MIN_DELAY_SEC

        return max(MIN_DELAY_SEC, min(delay, MAX_DELAY_SEC))

    def exponential_backoff_delay(self, elapsed_time_sec: int) -> float:
        return min(MIN_DELAY_SEC * (2 ** (elapsed_time_sec - 1)), MAX_DELAY_SEC)

    def fixed_delay(self) -> float:
        return (MIN_DELAY_SEC + MAX_DELAY_SEC) / 3
