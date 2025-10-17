from fastapi import APIRouter, Request
from app.models.schemas import VeracityRequest, VeracityResponse
from app.core.veracity_predictor import VeracityPredictor
import os
import logging
import json_log_formatter
import time
from datetime import datetime

# Tạo formatter hỗ trợ Unicode
class CustomJsonFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra["message"] = message
        extra["time"] = datetime.utcnow().isoformat()
        return extra

# Tạo thư mục logs nếu chưa có
os.makedirs("logs", exist_ok=True)

# Cấu hình logger
formatter = CustomJsonFormatter()
logfile = logging.FileHandler("logs/api.log", encoding="utf-8")
logfile.setFormatter(formatter)

logger = logging.getLogger("veracity_logger")
logger.setLevel(logging.INFO)
logger.addHandler(logfile)

router = APIRouter()

@router.post("/", response_model=VeracityResponse)
async def predict(request_data: VeracityRequest, request: Request):
    start_time = time.time()
    predictor = request.app.veracity_predictor
    label = predictor.predict(request_data.claim, request_data.evidence)
    prediction_time = round(time.time() - start_time, 3)

    # Log JSON với tiếng Việt
    logger.info("Prediction", extra={
        "claim": request_data.claim,
        "evidence": request_data.evidence,
        "label": label,
        "prediction_time": prediction_time
    })

    return VeracityResponse(label=label)
