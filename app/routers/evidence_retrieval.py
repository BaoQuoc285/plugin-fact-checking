from fastapi import APIRouter
from app.models.schemas import EvidenceRequest, EvidenceResponse
from app.core.evidence_retriever import EvidenceRetriever
# Initialize the EvidenceRetriever with a dummy API key
evidence_retriever = EvidenceRetriever(search_api_key="297e5175d5055b5816ceb37fe503851598633097", num_results=5)

router = APIRouter()

@router.post("/", response_model=EvidenceResponse)
async def retrieve_evidence(request: EvidenceRequest):
    """
    Retrieve evidence based on the provided query.
    
    Args:
        request (EvidenceRequest): The request containing the query and number of results.
    
    Returns:
        EvidenceResponse: The response containing the retrieved evidence.
    """
    evidence = evidence_retriever.retrieve_evidence_with_raw_snippets(
        query=request.query,
        num_results=request.num_results,
    )
    
    return EvidenceResponse(evidence=evidence)