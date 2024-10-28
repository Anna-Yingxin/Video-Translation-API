import asyncio
import time
import random
from typing import Optional, Callable, Dict, Any

from fastapi import HTTPException
import structlog

from src.adaptive_delay import DelayStrategies
from src.server import get_video

logger = structlog.getLogger(__name__)


def estimate_translation_time(video_length_seconds) -> float:
    base_time = 3
    processing_factor = 0.5
    return base_time + (video_length_seconds * processing_factor)


class VideoTranslationClient:
    def __init__(
        self,
        video_length_seconds: Optional[int],
        retry_strategy_idx: int,
    ):
        self.max_retries = 3
        self.retry_strategy_idx = retry_strategy_idx
        self.video_length_seconds = video_length_seconds

        if self.video_length_seconds:
            self.delay_strategies = DelayStrategies(
                estimate_translation_time(self.video_length_seconds),
            )

    def _calculate_delay(self, user_input: int, elapsed_time: float) -> float:
        if user_input == 0:
            delay = self.delay_strategies.fixed_delay()
        elif self.delay_strategies and user_input == 1:
            delay = self.delay_strategies.exponential_backoff_delay(elapsed_time)
        else:
            delay = self.delay_strategies.adaptive_delay(elapsed_time)

        delay *= 0.9 + random.random() * 0.2
        return delay

    async def wait_for_completion(
        self,
        file_id: str,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        attempt = 1

        while True:
            elapsed_time = time.time() - start_time

            if timeout and elapsed_time > timeout:
                raise TimeoutError(
                    f"Job {file_id} did not complete within {timeout} seconds"
                )

            try:
                if self.video_length_seconds:
                    data = await get_video(file_id, self.video_length_seconds)
                else:
                    data = await get_video(file_id)

                if callback:
                    callback(data)

                if data["status"] == "completed":
                    return data

                delay = self._calculate_delay(self.retry_strategy_idx, elapsed_time)
                logger.info("Waiting before next poll", delay=f"{delay:.2f}")
                await asyncio.sleep(delay)

            except HTTPException as e:
                if 400 <= e.status_code < 500:
                    raise

                if attempt > self.max_retries:
                    raise

                delay = max(
                    self._calculate_delay(self.retry_strategy_idx, elapsed_time), 5
                )
                logger.warning(
                    "Retrying after error", error=str(e), delay=f"{delay:.2f}"
                )
                await asyncio.sleep(delay)
                attempt += 1

            except Exception as e:
                if attempt > self.max_retries:
                    raise

                delay = self._calculate_delay(self.retry_strategy_idx, elapsed_time)
                logger.warning(
                    "Retrying after unexpected error",
                    error=str(e),
                    delay=f"{delay:.2f}",
                )
                await asyncio.sleep(delay)
                attempt += 1
