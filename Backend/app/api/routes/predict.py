from fastapi import APIRouter, HTTPException
from app.schemas.predict_schema import PredictRequest, PredictResponse
from app.services.predict import predict_user, fetch_transactions, fetch_account_info, fetch_features

router = APIRouter(prefix="/predict", tags=["Prediction"])


# ================= PREDICT =================
@router.post("/", response_model=PredictResponse)
def predict(data: PredictRequest):
    try:
        result = predict_user(data.account_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= TRANSACTIONS =================
@router.get("/transactions/{account_id}")
def get_transactions(account_id: str):
    try:
        return fetch_transactions(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= ACCOUNT INFO =================
@router.get("/account/{account_id}")
def get_account(account_id: str):
    try:
        return fetch_account_info(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= FEATURES =================
@router.get("/features/{account_id}")
def get_features(account_id: str):
    try:
        return fetch_features(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))