from fastapi import APIRouter
from app.schemas.predict_schema import PredictRequest
from app.services.predict import predict_user

router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("/")
def predict(data: PredictRequest):
    result = predict_user(data.dict())
    return result
