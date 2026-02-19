from pydantic import BaseModel


class UserInput(BaseModel):
    total_debit: float
    total_credit: float
    total_transactions: int

    food_spend: float
    shopping_spend: float
    transport_spend: float
    rent_spend: float
    emi_spend: float
    utility_spend: float

    upi_txn: int
    pos_txn: int
    neft_txn: int

    savings_ratio: float
    emi_ratio: float
    food_ratio: float
    digital_ratio: float
