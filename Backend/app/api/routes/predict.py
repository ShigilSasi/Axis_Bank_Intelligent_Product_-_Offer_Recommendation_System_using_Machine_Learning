from fastapi import APIRouter
from app.schemas.user_input import UserInput
from app.services.predict import predict_user

router = APIRouter()


@router.post("/predict")
def predict(data: UserInput):
    """
    Predict loan, card, offer and churn risk
    """

    # Convert schema → dict
    input_data = data.dict()

    # Call prediction engine
    result = predict_user(input_data)

    return result
