# Video Translation API with Polling Strategies

## Overview

This project provides an API for checking the status of video translations, offering different polling strategies to optimize the status-checking process.

- **`server.py`**: Defines a synchronous API with a GET endpoint where users can upload videos and check their translation status.
- **`endpoint.py`**: Simulates a video translation server endpoint, tracking video processing based on file ID and video length. It returns "pending" until the processing time elapses, then "completed," with a small chance of raising an HTTP 503 error to simulate server instability.
- **`adaptive_delay.py`**: Implements three polling delay strategies—fixed delay, exponential backoff, and adaptive delay. The adaptive strategy adjusts polling intervals based on estimated completion time, minimizing requests during early stages and increasing frequency as the process nears completion.
- **`client_library.py`**: Defines a client that polls the server for video translation completion status, using configurable delay strategies (fixed, exponential backoff, and adaptive). It includes error handling with retry logic, delay logging, and a callback option for real-time status updates.
- **`test_integration.py`**: Contains integration tests for the `VideoTranslationClient`, verifying different retry strategies, concurrent processing, timeout handling, oversized video handling, and callback invocation to ensure robust client functionality.
- **`use.py`**: A command-line script allowing users to initiate a video translation process by entering a file ID, optional video length, and the preferred retry strategy.

## Installation

Clone the repository and install the dependencies:

```console
git clone https://github.com/Anna-Yingxin/Video-Translation-API.git
cd Video-Translation-API
pip install -r requirements.txt
```

## Example Usage
Set the server URL and run the script:
```console
export SERVER_URL="http://your.url:8000"
python use.py
```
Below is an example of translating a video using the fixed delay polling strategy:

```
# User Input
Enter the job ID: 1
Enter video length in hours (e.g., 1.5 for 1.5 hours): 2

# Available Strategies
Available Polling Strategies:
0: Fixed delay (waits 4 seconds between each poll)
1: Exponential backoff (increases the wait time after each failed attempt)
2: Adaptive delay (calculates an estimated processing time and polls more frequently as it nears completion)

Please select a polling strategy by entering 0, 1, or 2: 0
You selected: Fixed delay (waits 4 seconds between each poll)

# Processing Output
Initiating video translation process...
2024-10-28 20:59:17 [info     ] Waiting before next poll. Need to wait 10.82 seconds until the next poll.
2024-10-28 20:59:28 [info     ] Waiting before next poll. Need to wait 1.88 seconds until the next poll.
2024-10-28 20:59:30 [info     ] Waiting before next poll. Need to wait 2.05 seconds until the next poll.
... [processing continues]
2024-10-28 20:59:43 [info    ] File status retrieved        file_id=1 status=completed

# Result
✨ Translation completed successfully! ✨
✨ Result: {'file_id': '1', 'status': 'completed'} ✨
```
