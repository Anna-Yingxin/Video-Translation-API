class DelayStrategies:
    def __init__(
        self,
        estimated_translation_time,
    ):
        self.min_delay = 2.0
        self.max_delay = 10.0

        self.early_phase_end = 70.0
        self.mid_phase_end = 90.0

        self.estimated_translation_time = estimated_translation_time

    def adaptive_delay(self, elapsed_time: float) -> float:
        estimated_time = self.estimated_translation_time

        progress = min(100.0, (elapsed_time / estimated_time) * 100)

        if progress < self.early_phase_end:
            delay = self.max_delay * (1 - progress / self.early_phase_end)
        elif progress < self.mid_phase_end:
            mid_progress = (progress - self.early_phase_end) / (
                self.mid_phase_end - self.early_phase_end
            )
            delay = self.max_delay * 0.5 * (1 - mid_progress)
        else:
            delay = self.min_delay

        return max(self.min_delay, min(delay, self.max_delay))

    def exponential_backoff_delay(self, elapsed_time: float) -> float:
        return min(self.min_delay * (2 ** (elapsed_time - 1)), self.max_delay)

    def fixed_delay(self) -> float:
        return (self.min_delay + self.max_delay) / 3
