CREATE TABLE account_info (
    account_id VARCHAR PRIMARY KEY,
    account_holder VARCHAR,
    account_number VARCHAR,
    ifsc VARCHAR,
    branch VARCHAR,
    currency VARCHAR,
    statement_start DATE,
    statement_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    txn_id SERIAL PRIMARY KEY,
    account_id VARCHAR REFERENCES account_info(account_id),
    txn_date DATE,
    narration TEXT,
    channel VARCHAR,
    merchant VARCHAR,
    category VARCHAR,
    debit NUMERIC,
    credit NUMERIC,
    balance NUMERIC
);

CREATE TABLE features (
    account_id VARCHAR PRIMARY KEY,
    total_debit NUMERIC,
    total_credit NUMERIC,
    total_transactions INT,
    food_spend NUMERIC,
    shopping_spend NUMERIC,
    transport_spend NUMERIC,
    rent_spend NUMERIC,
    emi_spend NUMERIC,
    utility_spend NUMERIC,
    upi_txn INT,
    pos_txn INT,
    neft_txn INT,
    top_merchant VARCHAR,
    savings_ratio FLOAT,
    emi_ratio FLOAT,
    food_ratio FLOAT,
    digital_ratio FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clusters (
    account_id VARCHAR PRIMARY KEY REFERENCES account_info(account_id),
    cluster INT,
    cluster_label VARCHAR,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE predictions (
    account_id VARCHAR PRIMARY KEY REFERENCES account_info(account_id),
    loan_eligible INT,
    card_suitable INT,
    offer_eligible INT,
    churn_risk INT,
    churn_probability FLOAT,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


SELECT * FROM account_info;