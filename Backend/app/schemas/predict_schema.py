from pydantic import BaseModel

class PredictRequest(BaseModel):
    account_id: str
