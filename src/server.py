import structlog
from fastapi import FastAPI, HTTPException
import requests

from src.endpoint import simulate_endpoint

app = FastAPI()

logger = structlog.getLogger(__name__)


@app.get("/check_status/{file_id}")
def get_video(file_id: str, video_length_hour: float):
    logger.info("Received video translation input", file_id=file_id)

    if video_length_hour > 2:
        raise HTTPException(
            status_code=413, detail="File size exceeds the allowed limit"
        )

    try:
        file_id, status = simulate_endpoint(file_id, video_length_hour)
        logger.info("File status retrieved", file_id=file_id, status=status)
        return {"file_id": file_id, "status": status}

    except HTTPException as e:
        logger.exception("Business error occurred", file_id=file_id, detail=str(e))
        raise

    except Exception as e:
        logger.exception("System error occurred", file_id=file_id)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
