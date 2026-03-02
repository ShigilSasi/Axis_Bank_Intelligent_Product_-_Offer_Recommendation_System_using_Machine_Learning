import pandas as pd
import numpy as np
import psycopg2
import os
from app.models.model_loader import models


# ================= FEATURE ORDER =================
FEATURES = [
    'total_debit', 'total_credit', 'total_transactions',
    'food_spend', 'shopping_spend', 'transport_spend',
    'rent_spend', 'emi_spend', 'utility_spend',
    'upi_txn', 'pos_txn', 'neft_txn',
    'savings_ratio', 'emi_ratio', 'food_ratio', 'digital_ratio'
]

MODEL_FEATURES = FEATURES + ['cluster']


# ================= CLUSTER LABEL MAP =================
cluster_name_map = {
    0: "Affluent Borrowers",
    1: "Conservative Savers",
    2: "Digital Lifestyle Spenders",
    3: "Stable Mass Market"
}


# ================= DB CONNECTION =================
def get_db_connection():
    return psycopg2.connect(
        host="shigil-pc.cfei2y0gokv7.ap-south-1.rds.amazonaws.com",
        database="Axis_Bank",
        user="postgres",
        password="Shigil-2000",
        port=5432,
        connect_timeout=5
    )


# ================= FETCH FEATURES FROM DB =================
def fetch_features(account_id: str) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                total_debit, total_credit, total_transactions,
                food_spend, shopping_spend, transport_spend,
                rent_spend, emi_spend, utility_spend,
                upi_txn, pos_txn, neft_txn,
                savings_ratio, emi_ratio, food_ratio, digital_ratio
            FROM features
            WHERE account_id = %s
        """, (account_id,))

        row = cur.fetchone()

        if row is None:
            raise ValueError(f"No features found for account_id: {account_id}")

        # Map to dict using FEATURES order
        return dict(zip(FEATURES, row))

    finally:
        conn.close()


# ================= FETCH TRANSACTIONS FROM DB =================
def fetch_transactions(account_id: str) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                txn_date, narration, channel,
                merchant, category, debit, credit, balance
            FROM transactions
            WHERE account_id = %s
            ORDER BY txn_date DESC
        """, (account_id,))

        rows = cur.fetchall()
        columns = ['txn_date', 'narration', 'channel',
                   'merchant', 'category', 'debit', 'credit', 'balance']
        return [dict(zip(columns, row)) for row in rows]

    finally:
        conn.close()


# ================= FETCH ACCOUNT INFO FROM DB =================
def fetch_account_info(account_id: str) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                account_holder, account_number, account_type,
                ifsc, branch, currency, statement_period,
                statement_start, statement_end, customer_id
            FROM account_info
            WHERE account_id = %s
        """, (account_id,))

        row = cur.fetchone()

        if row is None:
            raise ValueError(f"No account found for account_id: {account_id}")

        columns = ['account_holder', 'account_number', 'account_type',
                   'ifsc', 'branch', 'currency', 'statement_period',
                   'statement_start', 'statement_end', 'customer_id']
        return dict(zip(columns, row))

    finally:
        conn.close()


# ================= RECOMMENDATION ENGINE =================
def recommend_products(row):
    recommendations = {
        "credit_cards": [],
        "loans": [],
        "offers": []
    }

    total_debit = max(row['total_debit'], 1)

    # ================= CREDIT CARDS =================
    if row['shopping_spend'] > 0.22 * total_debit and row['digital_ratio'] > 0.60 and row['total_credit'] > 400000:
        recommendations['credit_cards'].append("Shopping Rewards Credit Card")

    if row['food_ratio'] > 0.09 and row['total_transactions'] > 600:
        recommendations['credit_cards'].append("Dining Cashback Card")

    if row['transport_spend'] > 0.15 * total_debit and row['total_credit'] > 500000:
        recommendations['credit_cards'].append("Fuel Benefits Card")

    if row['digital_ratio'] > 0.80 and row['upi_txn'] > 200 and row['total_credit'] > 600000:
        recommendations['credit_cards'].append("Digital Cashback Card")

    if row['total_credit'] < 300000 and row['total_transactions'] > 400 and row['digital_ratio'] > 0.50:
        recommendations['credit_cards'].append("Secured Credit Card")

    # ================= LOANS =================
    if row['total_credit'] > 2_500_000 and row['emi_ratio'] < 0.18 and row['savings_ratio'] > 1.3:
        recommendations['loans'].append("Pre-approved Personal Loan")

    elif row['emi_spend'] == 0 and row['total_credit'] > 1_000_000:
        recommendations['loans'].append("Instant Personal Loan")

    elif row['savings_ratio'] < 0.6 and 500000 < row['total_credit'] < 1_500_000:
        recommendations['loans'].append("Short-term Digital Loan")

    elif row['emi_spend'] > 600000 and row['emi_ratio'] < 0.45:
        recommendations['loans'].append("Top-up Loan")

    # ================= OFFERS =================
    if row['upi_txn'] > 250 and row['digital_ratio'] > 0.75 and row['total_transactions'] > 700:
        recommendations['offers'].append("UPI Cashback Offer")

    if row['shopping_spend'] > 180000 and row['shopping_spend'] > 0.25 * total_debit and row['digital_ratio'] > 0.60:
        recommendations['offers'].append("Shopping Cashback Offer")

    if row['utility_spend'] > 90000 and row['savings_ratio'] > 1:
        recommendations['offers'].append("Utility Cashback Offer")

    if row['food_ratio'] > 0.12 and row['total_transactions'] > 800 and row['digital_ratio'] > 0.60:
        recommendations['offers'].append("Dining Discount Offer")

    return recommendations


# ================= MAIN PREDICT FUNCTION =================
def predict_user(account_id: str):

    # ---------- Step 1: Fetch features from DB ----------
    input_data = fetch_features(account_id)

    scaler      = models["scaler_model"]
    kmeans      = models["kmeans_model"]
    loan_model  = models["loan_model"]
    card_model  = models["card_model"]
    offer_model = models["offer_model"]
    churn_model = models["churn_model"]

    df = pd.DataFrame([input_data])

    # ---------- Step 2: Cluster ----------
    X_scaled = scaler.transform(df[FEATURES])
    cluster  = kmeans.predict(X_scaled)[0]
    df['cluster'] = cluster

    # ---------- Step 3: Supervised ML ----------
    X_model    = df[MODEL_FEATURES]
    loan_pred  = int(loan_model.predict(X_model)[0])
    card_pred  = int(card_model.predict(X_model)[0])
    offer_pred = int(offer_model.predict(X_model)[0])
    churn_pred = int(churn_model.predict(X_model)[0])
    churn_prob = float(churn_model.predict_proba(X_model)[0][1])

    # ---------- Step 4: Recommendations ----------
    recommendations = recommend_products(df.iloc[0])

    # ---------- Step 5: Return ----------
    return {
        "account_id":        account_id,
        "cluster":           int(cluster),
        "cluster_label":     cluster_name_map.get(int(cluster), "Unknown"),
        "loan_eligible":     1 if len(recommendations['loans']) > 0        else loan_pred,
        "card_suitable":     1 if len(recommendations['credit_cards']) > 0 else card_pred,
        "offer_eligible":    1 if len(recommendations['offers']) > 0       else offer_pred,
        "churn_risk":        churn_pred,
        "churn_probability": churn_prob,
        "recommendations":   recommendations
    }