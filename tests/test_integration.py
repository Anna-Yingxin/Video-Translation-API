import pytest
import requests
import time
from src.client_library import VideoTranslationClient
from src.adaptive_delay import DelayStrategies


@pytest.fixture
def client_fixed_delay():
    """Client setup using fixed delay strategy (index 0)."""
    return VideoTranslationClient(video_length_hour=0.4, retry_strategy_idx=0)


@pytest.fixture
def client_exponential_backoff_delay():
    """Client setup using exponential backoff delay strategy (index 1)."""
    return VideoTranslationClient(video_length_hour=0.4, retry_strategy_idx=1)


@pytest.fixture
def client_adaptive_delay():
    """Client setup using adaptive delay strategy (index 2)."""
    return VideoTranslationClient(video_length_hour=0.4, retry_strategy_idx=2)


def test_status_completed_fixed_delay(client_fixed_delay):
    file_id = "test_file_fixed"
    status = None
    delays = []

    while status != "completed":
        start_time = time.time()
        response = client_fixed_delay.wait_for_completion(file_id)
        end_time = time.time()

        status = response["status"]
        delays.append(end_time - start_time)

        if status == "completed":
            break

    expected_delay = DelayStrategies(10).fixed_delay()

    assert all(abs(d - expected_delay) < 0.2 for d in delays[1:])
    assert status == "completed"


def test_status_completed_exponential_backoff_delay(client_exponential_backoff_delay):
    file_id = "test_file_exponential"
    status = None
    delays = []
    attempt = 0

    while status != "completed":
        start_time = time.time()
        response = client_exponential_backoff_delay.wait_for_completion(file_id)
        end_time = time.time()

        status = response["status"]
        delay = end_time - start_time
        delays.append(delay)

        if status == "completed":
            break

        expected_delay = min(2**attempt, 10)
        assert abs(delay - expected_delay) < 0.2
        attempt += 1

    assert status == "completed"


def test_status_completed_adaptive_delay(client_adaptive_delay):
    file_id = "test_file_adaptive"
    status = None
    delays = []
    estimated_translation_time = 10
    delay_strategy = DelayStrategies(estimated_translation_time)

    elapsed_time = 0
    while status != "completed":
        start_time = time.time()
        response = client_adaptive_delay.wait_for_completion(file_id)
        end_time = time.time()

        status = response["status"]
        delay = end_time - start_time
        delays.append(delay)

        if status == "completed":
            break

        expected_delay = delay_strategy.adaptive_delay(elapsed_time)
        assert abs(delay - expected_delay) < 0.2
        elapsed_time += delay

    assert status == "completed"


def test_http_error_handling(client_fixed_delay):
    file_id = "test_file_error"
    invalid_length = 3.0

    response = requests.get(
        f"{client_fixed_delay.server_url}/check_status/{file_id}",
        params={"video_length_hour": invalid_length},
    )
    with pytest.raises(requests.HTTPError) as exc_info:
        response.raise_for_status()

    assert exc_info.value.response.status_code == 413
