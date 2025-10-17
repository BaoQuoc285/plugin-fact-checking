from fastapi import APIRouter
from app.models.schemas import ClaimRequest, ClaimResponse

router = APIRouter()

@router.post("/", response_model=ClaimResponse)
async def detect_claims(request: ClaimRequest):
    claims = [request.text]
    return {"claims": claims}
