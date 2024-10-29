import time
import random
import requests
import os
from typing import Dict, Any

import structlog

from src.adaptive_delay import DelayStrategies


logger = structlog.getLogger(__name__)

MAX_RETRY = 3
TIMEOUT_SEC = 300


def estimate_translation_time_sec(video_length_hour) -> float:
    base_time_sec = 3
    processing_factor = 0.6
    return base_time_sec + (video_length_hour * processing_factor)


class VideoTranslationClient:
    def __init__(
        self,
        video_length_hour: float,
        retry_strategy_idx: int,
    ):
        self.server_url = os.getenv("SERVER_URL", "http://127.0.0.1:8000")

        self.retry_strategy_idx = retry_strategy_idx
        self.video_length_hour = video_length_hour

        self.delay_strategies = DelayStrategies(
            estimate_translation_time_sec(self.video_length_hour),
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

    def wait_for_completion(
        self,
        file_id: str,
    ) -> Dict[str, Any]:
        start_time = time.time()
        attempt = 1
        time.sleep(1)

        while True:
            elapsed_time_sec = time.time() - start_time

            if elapsed_time_sec > TIMEOUT_SEC:
                raise TimeoutError(
                    f"Job {file_id} did not complete within {TIMEOUT_SEC} seconds"
                )

            try:
                response = requests.get(
                    f"{self.server_url}/check_status/{file_id}",
                    params={"video_length_hour": self.video_length_hour},
                )
                response.raise_for_status()
                data = response.json()

                if data["status"] == "completed":
                    return data

            except Exception as e:
                if isinstance(e, requests.HTTPError):
                    status_code = e.response.status_code
                    if 400 <= status_code < 500:
                        logger.error(
                            "Client error occurred",
                            status_code=status_code,
                            error=e.response.text,
                            file_id=file_id,
                        )
                        raise
                    else:
                        error_message = e.response.text
                else:
                    error_message = str(e)

                if attempt > MAX_RETRY:
                    logger.error(
                        "Max retries reached", error=error_message, file_id=file_id
                    )
                    raise

                delay = max(
                    self._calculate_delay(self.retry_strategy_idx, elapsed_time_sec), 5
                )
                logger.warning(
                    "Error occurred, retrying",
                    error_message=error_message,
                    attempt=attempt,
                    next_delay_time=f"{delay:.2f}",
                    file_id=file_id,
                )
                time.sleep(delay)
                attempt += 1
