from fastapi import APIRouter
from app.models.schemas import FactCheckRequest, FactCheckResponse
from app.core.factcheck import FactCheck  # Giả sử FactCheck là lớp thực hiện quy trình fact-check

router = APIRouter()

@router.post("/", response_model=FactCheckResponse)
async def full_fact_check(request: FactCheckRequest):
    # print(request.claim)
    claim = request.claim
    search_api_key = "API"
    model_path = "C://Users//PC//Downloads//app-20250612T075040Z-1-001//app//models//weights//model_pho_bert_base.pth"
    llm_api_key ={
        "provider": "GEMINI",
        "model_name": "gemini-2.0-flash",
        "api_key": "None"
    }
    selection_method ="bm25"  # Hoặc phương pháp khác nếu cần
    fact_checker = FactCheck(
        search_api_key=search_api_key,
        model_path=model_path,
        llm_api_params=llm_api_key,
        selector_method='bm25'  # Ví dụ: sử dụng phương pháp BM25 để chọn bằng chứng
    )
    result = fact_checker.check(claim, num_evidence=3, top_k=4)
    return FactCheckResponse(
        claim=result["claim"],
        evidences=result["evidences"],
        accuracy_percent=result["accuracy_percent"],
    )
