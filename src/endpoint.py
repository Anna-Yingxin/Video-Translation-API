from fastapi import HTTPException
import random
import time
from datetime import datetime
from typing import Tuple


video_tracker = {}


def simulate_endpoint(file_id, video_length_hour) -> Tuple[str, str]:
    if file_id not in video_tracker:
        video_tracker[file_id] = {
            "start_time": datetime.now(),
            "length": video_length_hour,
        }

    elapsed_time = (
        datetime.now() - video_tracker[file_id]["start_time"]
    ).total_seconds()

    if video_length_hour <= 0.3:
        completion_time = 3
        error_rate = 0
    elif video_length_hour <= 0.5:
        completion_time = 10
        error_rate = 0.01
    elif video_length_hour <= 1:
        completion_time = 16
        error_rate = 0.02
    elif video_length_hour <= 1.5:
        completion_time = 20
        error_rate = 0.02
    else:
        completion_time = 40
        error_rate = 0.03

    if random.random() < error_rate:
        time.sleep(3)
        raise HTTPException(status_code=503, detail="Unstable server connection")

    if elapsed_time < completion_time:
        return file_id, "pending"

    return file_id, "completed"
