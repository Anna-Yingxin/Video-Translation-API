from fastapi import HTTPException
import asyncio
from typing import Optional, Tuple
import sys

from src.client_library import VideoTranslationClient


def hours_to_seconds(hours: float) -> int:
    return int(hours * 3600)


async def get_user_input() -> Tuple[str, Optional[int], int]:
    # Get file ID
    while True:
        file_id = input("Enter the job ID: ").strip()
        if file_id:
            break
        print("Job ID cannot be empty")

    # Get video length
    while True:
        video_length = input(
            "Enter video length in hours (e.g., 1.5 for 1.5 hours, press Enter to skip): "
        ).strip()

        if not video_length:
            break

        try:
            hours = float(video_length)
            if hours <= 0:
                print("Video length must be positive")
                continue
            elif hours > 2:
                print("Video length must be less than or equal to 2 hours")
            break
        except ValueError:
            print("Please enter a valid number")

    # Get retry strategy
    retry_strategies = {
        0: "Fixed delay",
        1: "Exponential backoff",
        2: "Adaptive delay",
    }

    print("\nAvailable retry strategies:")
    for idx, strategy in retry_strategies.items():
        print(f"{idx}: {strategy}")

    while True:
        try:
            retry_strategy = input("\nSelect retry strategy (0-2): ").strip()
            retry_strategy_idx = int(retry_strategy)
            if retry_strategy_idx in retry_strategies:
                break
            print(f"Please enter a number between 0 and {len(retry_strategies)-1}")
        except ValueError:
            print("Please enter a valid number")

    return file_id, hours, retry_strategy_idx


async def process_video():
    try:
        input_file_id, video_length_seconds, retry_strategy_idx = await get_user_input()
        print("\nInitiating video translation process...")

        client = VideoTranslationClient(
            video_length_seconds=video_length_seconds,
            retry_strategy_idx=retry_strategy_idx,
        )

        def status_callback(status: str):
            print(f"Status: {status}", end="\r")

        result = await client.wait_for_completion(
            file_id=input_file_id,
            callback=status_callback,
            timeout=500,
        )

        print(f"\nTranslation completed successfully!")
        print(f"Result: {result}")
        return result

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except TimeoutError:
        print("\n\nJob timed out")
    except HTTPException as e:
        print(f"\n\nHTTP Status ({e.status_code}): {e.detail}")
    except Exception as e:
        print(f"\n\nError: {e}")

    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(process_video())
