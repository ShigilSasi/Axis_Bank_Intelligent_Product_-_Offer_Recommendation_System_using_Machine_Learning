import pandas as pd
import numpy as np

from app.models.model_loader import (
    scaler,
    kmeans,
    loan_model,
    card_model,
    offer_model,
    churn_model
)


FEATURES = [
    'total_debit', 'total_credit', 'total_transactions',
    'food_spend', 'shopping_spend', 'transport_spend',
    'rent_spend', 'emi_spend', 'utility_spend',
    'upi_txn', 'pos_txn', 'neft_txn',
    'savings_ratio', 'emi_ratio', 'food_ratio', 'digital_ratio'
]

MODEL_FEATURES = FEATURES + ['cluster']


# Recommendatation engine
def generate_recommendations(row):

    recommendations = {
        "credit_cards": [],
        "loans": [],
        "offers": []
    }

    total_debit = max(row['total_debit'], 1)

    # -------- CREDIT CARDS --------
    if row['shopping_spend'] > 0.22 * total_debit and row['digital_ratio'] > 0.60:
        recommendations['credit_cards'].append("Shopping Rewards Credit Card")

    if row['food_ratio'] > 0.09 and row['total_transactions'] > 600:
        recommendations['credit_cards'].append("Dining Cashback Card")

    if row['transport_spend'] > 0.15 * total_debit:
        recommendations['credit_cards'].append("Fuel Benefits Card")

    if row['digital_ratio'] > 0.80 and row['upi_txn'] > 200:
        recommendations['credit_cards'].append("Digital Cashback Card")

    # -------- LOANS --------
    if row['emi_ratio'] < 0.18 and row['savings_ratio'] > 1.3:
        recommendations['loans'].append("Pre-approved Personal Loan")

    elif row['emi_spend'] == 0 and row['total_credit'] > 1_000_000:
        recommendations['loans'].append("Instant Personal Loan")

    elif row['savings_ratio'] < 0.6:
        recommendations['loans'].append("Short-term Digital Loan")

    # -------- OFFERS --------
    if row['upi_txn'] > 250 and row['digital_ratio'] > 0.75:
        recommendations['offers'].append("UPI Cashback Offer")

    if row['shopping_spend'] > 0.25 * total_debit:
        recommendations['offers'].append("Shopping Cashback Offer")

    if row['utility_spend'] > 90000:
        recommendations['offers'].append("Utility Cashback Offer")

    return recommendations

# Main Prediction Function
def predict_user(input_data: dict):

    # ---------- 1. Convert to DataFrame ----------
    df = pd.DataFrame([input_data])

    # ---------- 2. Cluster Prediction ----------
    X_scaled = scaler.transform(df[FEATURES])
    cluster = kmeans.predict(X_scaled)[0]
    df['cluster'] = cluster

    # ---------- 3. Model Predictions ----------
    X_model = df[MODEL_FEATURES]

    loan_pred = int(loan_model.predict(X_model)[0])
    card_pred = int(card_model.predict(X_model)[0])
    offer_pred = int(offer_model.predict(X_model)[0])
    churn_pred = int(churn_model.predict(X_model)[0])

    churn_prob = float(churn_model.predict_proba(X_model)[0][1])

    # ---------- 4. Recommendation Engine ----------
    recommendations = generate_recommendations(df.iloc[0])

    # ---------- 5. Final Response ----------
    response = {
        "cluster": int(cluster),
        "loan_eligible": loan_pred,
        "card_suitable": card_pred,
        "offer_eligible": offer_pred,
        "churn_risk": churn_pred,
        "churn_probability": churn_prob,
        "recommendations": recommendations
    }

    return response