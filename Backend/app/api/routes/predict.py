from fastapi import APIRouter, HTTPException
from app.schemas.predict_schema import PredictRequest, PredictResponse
from app.services.predict import predict_user

router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("/", response_model=PredictResponse)
def predict(data: PredictRequest):
    try:
        result = predict_user(data.account_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))