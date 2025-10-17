from fastapi import APIRouter
from app.models.schemas import SelectionRequest, SelectionResponse, Snippet
from app.core.evidence_selection import get_selector

router = APIRouter()

@router.post("/", response_model=SelectionResponse)
async def evidence_selection(request: SelectionRequest):
    selector = get_selector(request.method or "bm25")

    # Chuyển contexts thành List[Tuple[text, source]]
    context_pairs = [(snippet.text, snippet.source) for snippet in request.contexts]

    selected_pairs = selector.select(claim=request.claim, contexts=context_pairs, top_k=request.k)

    return SelectionResponse(
        evidence=[Snippet(text=text, source=source) for text, source in selected_pairs]
    )

