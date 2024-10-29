import requests
from typing import Tuple
import sys

from src.client_library import VideoTranslationClient


def hours_to_seconds(hours: float) -> int:
    return int(hours * 3600)


def get_user_input() -> Tuple[str, float, int]:
    # Get file ID
    while True:
        file_id = input("🥝 Enter the job ID: ").strip()
        if file_id:
            break
        print("Job ID cannot be empty")

    # Get video length
    while True:
        video_length_hour = input(
            "\n🥝 Enter video length in hours (e.g., 1.5 for 1.5 hours): "
        ).strip()

        try:
            video_length_hour = float(video_length_hour)
            if video_length_hour <= 0:
                print("!! Video length must be a positive number.")
            elif video_length_hour > 2:
                print("!! Video length must be less than or equal to 2 hours.")
            else:
                break
        except ValueError:
            print("!! Please enter a valid number for the video length.")

    # Get retry strategy
    retry_strategies = {
        0: "Fixed delay (waits 4 seconds between each poll)",
        1: "Exponential backoff (increases the wait time after each failed attempt)",
        2: "Adaptive delay (calculates an estimated processing time and polls more frequently as it nears completion)",
    }

    print("\n🥝 Available Polling Strategies:")
    for idx, strategy in retry_strategies.items():
        print(f"{idx}: {strategy}")

    while True:
        try:
            retry_strategy = input(
                "\nPlease select a polling strategy by entering 0, 1, or 2: "
            ).strip()
            retry_strategy_idx = int(retry_strategy)
            if retry_strategy_idx in retry_strategies:
                print(f"You selected: {retry_strategies[retry_strategy_idx]}")
                break
            else:
                print(
                    f"!! Invalid choice. Enter a number between 0 and {len(retry_strategies) - 1}."
                )
        except ValueError:
            print("!! Invalid input. Please enter a number (0, 1, or 2).")

    return file_id, video_length_hour, retry_strategy_idx


def process_video():
    try:
        input_file_id, video_length_hour, retry_strategy_idx = get_user_input()
        print("\nInitiating video translation process...")

        client = VideoTranslationClient(
            video_length_hour=video_length_hour,
            retry_strategy_idx=retry_strategy_idx,
        )

        result = client.wait_for_completion(
            file_id=input_file_id,
        )

        print(f"\n\033[95m===========================================\033[0m")
        print(f"\033[95m★ Translation completed successfully! ★\033[0m")
        print(f"\033[32m→ Result: {result}\033[0m")
        print(f"\033[95m===========================================\033[0m")
        return result

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except TimeoutError:
        print("\n\nTranslation failed due to timed out")
    except requests.HTTPError as e:
        print(
            f"\n\nTranslation failed with HTTP Status ({e.response.status_code}): {e.response.text}"
        )
    except Exception as e:
        print(f"\n\nTranslation failed with: {e}")

    sys.exit(1)


if __name__ == "__main__":
    process_video()
