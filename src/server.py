import structlog
from fastapi import FastAPI, HTTPException
from typing import Optional

from src.endpoint import endpoint_simulate


app = FastAPI()

logger = structlog.getLogger(__name__)


@app.get("/check_status/{file_id}")
async def get_video(file_id: str, video_length_seconds: Optional[float]):
    try:
        logger.info("Received video translation input", file_id=file_id)

        if video_length_seconds and video_length_seconds > 2:
            raise HTTPException(
                status_code=413, detail="File size exceeds the allowed limit"
            )

        file_id, status = endpoint_simulate(file_id, video_length_seconds)

        logger.info("File status retrieved", file_id=file_id, status=status)
        return {"file_id": file_id, "status": status}

    except HTTPException:
        logger.exception("Business error occurred", file_id=file_id)
        raise

    except Exception:
        logger.exception("System error occurred", file_id=file_id)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
