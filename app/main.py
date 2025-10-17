from fastapi import FastAPI
from app.routers import factcheck
# from app.routers import claim_detection, evidence_retrieval, veracity_prediction, evidence_selection
import os
from app.core.veracity_predictor import VeracityPredictor
# main.py
import logging
import json_log_formatter

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
#PORT 9000
app = FastAPI(title="Fact Check Editor API")

@app.on_event("startup")
def load_model_once():
    #Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting Fact Check Editor API")
    logger.info("Loading model...")
    model_path="C://Users//PC//Downloads//app-20250612T075040Z-1-001//app//models//weights//model_pho_bert_base.pth"
    # model_path = "C://Users//ADMIN//Desktop//IE403-PluginFactChecking//app//models//weights//model_pho_bert_base.pth"
    predictor = VeracityPredictor(model_path)
    app.veracity_predictor = predictor  # Attach vào app
    logger.info("Model loaded successfully")

# Đăng ký các router
app.include_router(factcheck.router, prefix="/api/fact-check", tags=["Fact Check"])
# app.include_router(claim_detection.router, prefix="/api/claim-detection", tags=["Claim Detection"])
# app.include_router(evidence_retrieval.router, prefix="/api/evidence-retrieval", tags=["Evidence Retrieval"])
# app.include_router(veracity_prediction.router, prefix="/api/veracity-prediction", tags=["Veracity Prediction"])
# app.include_router(evidence_selection.router, prefix="/api/evidence-selection", tags=["Evidence Selection"])
# Đăng ký router cho trang chủ
@app.get("/")
def home():
    return {"message": "Fact Check Editor API is running"}
