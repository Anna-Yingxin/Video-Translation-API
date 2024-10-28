import asyncio
import pytest
import time
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager

from src.server import app
from src.client_library import VideoTranslationClient
from src.endpoint import video_tracker

@pytest.fixture
def test_client():
    client = TestClient(app)
    yield client
    video_tracker.clear()

@asynccontextmanager
async def assert_completion_time(min_time, max_time):
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    assert min_time <= elapsed_time <= max_time, \
        f"Operation took {elapsed_time:.2f}s, expected between {min_time:.2f}s and {max_time:.2f}s"

@pytest.mark.asyncio
class TestVideoTranslationIntegration:
    async def test_retry_strategies(self, test_client):
        video_lengths = [0.3, 0.5, 1.0, 1.5]
        strategies = ["Fixed interval", "Exponential backoff", "Adaptive delay"]
        
        for strategy_idx, strategy in enumerate(strategies):
            for video_length in video_lengths:
                client = VideoTranslationClient(video_length_seconds=video_length, retry_strategy_idx=strategy_idx)
                success_count = 0
                
                for _ in range(3):
                    try:
                        await client.wait_for_completion(f"{strategy}_len_{video_length}")
                        success_count += 1
                    except Exception:
                        pass
                success_rate = success_count / 3
                
                assert success_rate >= 0.66

    async def test_concurrent_processing(self, test_client):
        lengths_strategies = [(0.3, 0), (0.3, 1), (0.5, 1), (0.5, 2)]
        tasks = [
            VideoTranslationClient(video_length_seconds=length, retry_strategy_idx=strategy)
            .wait_for_completion(f"concurrent_{length}_{strategy}")
            for length, strategy in lengths_strategies
        ]
        
        results = await asyncio.gather(*tasks)
        assert all(result["status"] == "completed" for result in results)

    async def test_timeout(self, test_client):
        client = VideoTranslationClient(video_length_seconds=1.5, retry_strategy_idx=0)
        with pytest.raises(TimeoutError):
            await client.wait_for_completion("timeout_test", timeout=5.0)

    async def test_oversized_video(self, test_client):
        client = VideoTranslationClient(video_length_seconds=2.5, retry_strategy_idx=0)
        with pytest.raises(Exception) as exc_info:
            await client.wait_for_completion("oversized_test")
        assert "413" in str(exc_info.value)

    async def test_callback_invocation(self, test_client):
        status_updates = []
        
        def callback(data):
            status_updates.append(data["status"])
        
        client = VideoTranslationClient(video_length_seconds=0.5, retry_strategy_idx=0)
        await client.wait_for_completion("callback_test", callback=callback)
        
        assert "pending" in status_updates
        assert status_updates[-1] == "completed"