from pydantic import BaseModel
from typing import List, Dict

# ================= INPUT =================
class PredictRequest(BaseModel):
    account_id: str

# ================= OUTPUT =================
class RecommendationResponse(BaseModel):
    credit_cards: List[str]
    loans: List[str]
    offers: List[str]

class PredictResponse(BaseModel):
    account_id: str
    cluster: int
    cluster_label: str
    loan_eligible: int
    card_suitable: int
    offer_eligible: int
    churn_risk: int
    churn_probability: float
    recommendations: Dict[str, List[str]]