from typing import List, Optional
from pydantic import BaseModel

class ClaimRequest(BaseModel):
    text: str
    lang: Optional[str] = "vi"

class ClaimResponse(BaseModel):
    claims: List[str]

class EvidenceRequest(BaseModel):
    query: str
    num_results: Optional[int] = 5
    
class EvidenceItem(BaseModel):
    text: str
    source: str

class EvidenceResponse(BaseModel):
    evidence: List[EvidenceItem]

class VeracityRequest(BaseModel):
    claim: str =""
    evidence: str =""

class VeracityResponse(BaseModel):
    label: str

class FactCheckRequest(BaseModel):
    claim: str


class Evidence(BaseModel):
    source: str
    evidence: str
    label: str

class FactCheckResponse(BaseModel):
    claim: str
    evidences: List[Evidence]
    accuracy_percent: float
    # explanation: Optional[str]

class Snippet(BaseModel):
    text: str
    source: Optional[str] = None

class SelectionRequest(BaseModel):
    claim: str
    contexts: List[Snippet]  # mỗi context có text + source
    k: int = 5
    method: Optional[str] = "bm25"

class SelectionResponse(BaseModel):
    evidence: List[Snippet]  # trả lại các đoạn đã chọn kèm source