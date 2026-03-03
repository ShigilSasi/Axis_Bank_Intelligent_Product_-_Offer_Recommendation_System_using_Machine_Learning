# 🏦 Axis Bank — Smart Banking Intelligence Platform

> AI-powered bank statement analysis with customer segmentation, churn prediction, and personalized product recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-S3%20%2B%20Lambda-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Machine Learning](#-machine-learning)
- [AWS Infrastructure](#-aws-infrastructure)
- [PostgreSQL Database](#-postgresql-database)
- [FastAPI Backend](#-fastapi-backend)
- [Streamlit Frontend](#-streamlit-frontend)
- [Project Structure](#-project-structure)
- [Environment Setup](#-environment-setup)
- [Quick Start](#-quick-start)
- [Troubleshooting](#-troubleshooting)

---

## 🧠 Overview

The **Axis Bank Smart Banking Intelligence Platform** is an end-to-end ML system that:

- 📄 Accepts Axis Bank PDF statements via a web UI
- ☁️ Processes them automatically via AWS Lambda
- 🗃️ Stores structured data in PostgreSQL
- 🤖 Runs 6 ML models to generate predictions
- 📊 Displays a rich 5-tab analytics dashboard
- 🎯 Delivers personalized credit card, loan & offer recommendations

---

## 🏗️ Architecture

```
User (Browser)
    │
    ▼
Streamlit Frontend  ──── boto3 ────▶  AWS S3 (uploads/)
    │                                       │
    │                                  S3 Event Trigger
    │                                       │
    │                                       ▼
    │                               AWS Lambda (ETL)
    │                                  │        │
    │                                  ▼        ▼
    │                            PostgreSQL   S3 (processed/)
    │                                  │        │
    │◀──── FastAPI REST API ───────────┘        │
    │          (ML predictions)                 │
    │◀──────────────────────────────────────────┘
    │         (poll for account_id)
    ▼
Dashboard (5 tabs)
```

### Full Pipeline

| Step | Action | Service |
|------|--------|---------|
| 1 | User uploads PDF | Streamlit → S3 `uploads/` |
| 2 | S3 event fires | S3 → Lambda trigger |
| 3 | Lambda parses PDF | pdfplumber extraction |
| 4 | Data inserted | Lambda → PostgreSQL |
| 5 | JSON + CSV saved | Lambda → S3 `processed/` |
| 6 | Streamlit polls | S3 `processed/` for new JSON |
| 7 | Predictions fetched | Streamlit → FastAPI `/predict/` |
| 8 | Dashboard renders | 5-tab analytics UI |

---

## 🤖 Machine Learning

### 6 Models

| Model | Algorithm | Output |
|-------|-----------|--------|
| Customer Segmentation | KMeans (k=4) | Cluster ID + Label |
| Churn Prediction | Random Forest | Probability (0.0–1.0) |
| Credit Card Eligibility | Logistic Regression | Binary (0 or 1) |
| Loan Eligibility | Gradient Boosting | Binary (0 or 1) |
| Offer Eligibility | Logistic Regression | Binary (0 or 1) |
| Feature Engineering | Rule-based | 13 numerical features |

---

### Customer Segments

| Cluster | Segment | Description |
|---------|---------|-------------|
| 0 | **Affluent Borrowers** | High income, active EMI repayment, high credit utilisation |
| 1 | **Conservative Savers** | Low spenders, high savings ratio, minimal digital footprint |
| 2 | **Digital Lifestyle Spenders** | Heavy UPI/POS usage, lifestyle-oriented spending |
| 3 | **Stable Mass Market** | Balanced profile with moderate income and spending |

---

### Feature Engineering (13 Features)

| Feature | Formula |
|---------|---------|
| `total_debit` | Sum of all debit transactions |
| `total_credit` | Sum of all credit transactions |
| `txn_count` | Total number of transactions |
| `savings_ratio` | `total_credit / (total_debit + 1)` |
| `emi_ratio` | `emi_spend / (total_credit + 1)` |
| `food_ratio` | `food_spend / (total_debit + 1)` |
| `digital_ratio` | `(upi_txn + pos_txn) / (txn_count + 1)` |
| `upi_txn` | Count of UPI transactions |
| `pos_txn` | Count of POS / Card transactions |
| `neft_txn` | Count of NEFT transactions |
| `food_spend` | Sum of Food & Dining debits |
| `shopping_spend` | Sum of Shopping debits |
| `emi_spend` | Sum of Loan EMI debits |

---

### Churn Risk Bands

| Probability | Risk Level |
|-------------|------------|
| > 0.6 | 🔴 High Risk |
| 0.3 – 0.6 | 🟡 Medium Risk |
| < 0.3 | 🟢 Low Risk |

---

### Model Files

```
Backend/app/models/
├── kmeans_model.pkl      # Customer segmentation
├── churn_model.pkl       # Churn probability
├── card_model.pkl        # Credit card eligibility
├── loan_model.pkl        # Loan eligibility
├── offer_model.pkl       # Offer eligibility
└── scaler.pkl            # Feature normalisation
```

---

## ☁️ AWS Infrastructure

### S3 Bucket Structure

```
s3://bank-statement-upload-shigil/
├── uploads/
│   └── statement_920000000001.pdf      ← Streamlit uploads here
└── processed/
    ├── 920000000001_account_info.json  ← Lambda writes here
    └── 920000000001_transactions.csv
```

### Lambda Function

| Config | Value |
|--------|-------|
| Runtime | Python 3.11 |
| Timeout | 5 minutes |
| Memory | 512 MB |
| Trigger | `s3:ObjectCreated:*` on `uploads/` |
| Layers | `pdfplumber`, `psycopg2-binary` |
| Permissions | `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, RDS VPC access |

**Lambda ETL Steps:**
1. Read PDF from S3 via `boto3.get_object()`
2. Extract text with `pdfplumber`
3. Parse account info (number, holder, branch, IFSC, period)
4. Parse all transactions (date, narration, debit, credit, balance)
5. Categorise transactions via keyword regex rules
6. Assign payment channel (UPI / NEFT / RTGS / POS / CARD)
7. Bulk-insert into PostgreSQL via `psycopg2`
8. Write `account_info.json` + `transactions.csv` to S3 `processed/`

### IAM Policy (Minimum Required)

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket",
    "rds-db:connect",
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "*"
}
```

> ⚠️ Use a dedicated IAM user for the Streamlit frontend — **never use root credentials**. Grant `AmazonS3FullAccess` only.

---

## 🗃️ PostgreSQL Database

### Connection

| Property | Value |
|----------|-------|
| Host | `shigil-pc.cfei2y0gokv7.ap-south-1.rds.amazonaws.com` |
| Database | `Axis_Bank` |
| Port | `5432` |
| Engine | PostgreSQL 15 |

---

### Schema — 5 Tables

#### `accounts`
| Column | Type | Description |
|--------|------|-------------|
| `account_number` | `VARCHAR(20) PK` | Unique account ID |
| `account_holder` | `VARCHAR(100)` | Full name |
| `account_type` | `VARCHAR(50)` | Savings / Current |
| `branch` | `VARCHAR(100)` | Branch name |
| `ifsc` | `VARCHAR(20)` | IFSC code |
| `statement_period` | `VARCHAR(100)` | Date range of statement |
| `created_at` | `TIMESTAMP` | Record creation time |

#### `transactions`
| Column | Type | Description |
|--------|------|-------------|
| `id` | `SERIAL PK` | Auto-increment ID |
| `account_number` | `VARCHAR(20) FK` | Links to accounts |
| `txn_date` | `DATE` | Transaction date |
| `narration` | `TEXT` | Raw bank narration |
| `merchant` | `VARCHAR(100)` | Extracted merchant |
| `category` | `VARCHAR(50)` | Spending category |
| `channel` | `VARCHAR(30)` | UPI / NEFT / POS / CARD |
| `debit` | `NUMERIC(15,2)` | Debit amount |
| `credit` | `NUMERIC(15,2)` | Credit amount |
| `balance` | `NUMERIC(15,2)` | Running balance |

#### `features`
| Column | Type |
|--------|------|
| `account_number` | `VARCHAR(20) PK FK` |
| `total_debit` | `NUMERIC(15,2)` |
| `total_credit` | `NUMERIC(15,2)` |
| `txn_count` | `INTEGER` |
| `savings_ratio` | `NUMERIC(10,6)` |
| `emi_ratio` | `NUMERIC(10,6)` |
| `digital_ratio` | `NUMERIC(10,6)` |
| `food_spend` | `NUMERIC(15,2)` |
| `upi_txn` | `INTEGER` |
| `pos_txn` | `INTEGER` |
| `neft_txn` | `INTEGER` |

#### `predictions`
| Column | Type | Description |
|--------|------|-------------|
| `account_number` | `VARCHAR(20) PK FK` | Account reference |
| `cluster` | `INTEGER` | KMeans cluster ID (0–3) |
| `cluster_label` | `VARCHAR(100)` | Segment name |
| `churn_probability` | `NUMERIC(5,4)` | Churn probability 0.0–1.0 |
| `churn_risk` | `INTEGER` | 1 = high risk |
| `card_suitable` | `INTEGER` | 1 = eligible |
| `loan_eligible` | `INTEGER` | 1 = eligible |
| `offer_eligible` | `INTEGER` | 1 = eligible |
| `predicted_at` | `TIMESTAMP` | Prediction time |

#### `recommendations`
| Column | Type | Description |
|--------|------|-------------|
| `account_number` | `VARCHAR(20) FK` | Account reference |
| `rec_type` | `VARCHAR(20)` | `credit_card` / `loan` / `offer` |
| `product_name` | `VARCHAR(100)` | Product display name |
| `created_at` | `TIMESTAMP` | Generation time |

---

### Useful Queries

```sql
-- All transactions for an account
SELECT * FROM transactions
WHERE account_number = '920000000001'
ORDER BY txn_date DESC;

-- Predictions + recommendations
SELECT p.*, r.rec_type, r.product_name
FROM predictions p
LEFT JOIN recommendations r USING (account_number)
WHERE p.account_number = '920000000001';

-- Spending by category
SELECT category, SUM(debit) AS total_spend
FROM transactions
WHERE account_number = '920000000001'
GROUP BY category
ORDER BY total_spend DESC;
```

---

## ⚡ FastAPI Backend

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/` | Run all ML models for `account_id` |
| `GET` | `/predict/transactions/{account_id}` | Fetch all transactions |
| `GET` | `/predict/account/{account_id}` | Fetch account info |
| `GET` | `/predict/features/{account_id}` | Fetch computed features |
| `GET` | `/health` | Health check |

### Sample Request / Response

```bash
POST /predict/
Content-Type: application/json

{ "account_id": "920000000001" }
```

```json
{
  "cluster": 2,
  "cluster_label": "Digital Lifestyle Spenders",
  "churn_probability": 0.34,
  "churn_risk": 0,
  "card_suitable": 1,
  "loan_eligible": 0,
  "offer_eligible": 1,
  "recommendations": {
    "credit_cards": ["Digital Cashback Card"],
    "loans": [],
    "offers": ["UPI Cashback Offer"]
  }
}
```

### Run Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Docs at: http://127.0.0.1:8000/docs
```

---

## 🎨 Streamlit Frontend

### Dashboard Tabs

| Tab | Content |
|-----|---------|
| 🏠 Overview | Account card, total credit/debit, transaction count, segment label |
| 📊 Transactions | Spending pie, monthly bar, balance line, top merchants, filterable table |
| 🔬 Features | Spend distribution, channel donut, ratio bars, category heatmap |
| 🤖 ML Insights | Cluster card, churn gauge, eligibility badges, vs-cluster comparison |
| 🎯 Recommendations | Personalised credit cards, loans, cashback offers |

### Key Implementation Details

**Session State** — All data is cleared before each new PDF load to prevent stale data:

```python
def clear_session():
    st.session_state.predictions  = None
    st.session_state.transactions = None
    st.session_state.account_info = None
    st.session_state.account_id   = None
    st.session_state.active_tab   = "overview"
```

**Smart S3 Polling** — Records `upload_time` before S3 upload, then only considers JSONs with `LastModified >= upload_time - 5s` to always load the correct new account:

```python
def poll_for_account_id(filename, retries=20, delay=3):
    upload_time = time.time()
    # Only picks JSON files created AFTER this upload
    new_jsons = [o for o in contents
                 if o["LastModified"].timestamp() >= upload_time - 5]
```

**Manual Fallback** — If Lambda polling times out, users can enter their Account ID directly on the Upload page.

### Run Frontend

```bash
cd Frontend
pip install -r requirements.txt
streamlit run app.py
# Opens at: http://localhost:8501
```

---

## 📁 Project Structure

```
Axis-Bank-Intelligence/
│
├── Backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── predict.py       # API endpoints
│   │   ├── services/
│   │   │   └── predict.py           # DB queries + ML inference
│   │   └── models/                  # .pkl model files
│   │       ├── kmeans_model.pkl
│   │       ├── churn_model.pkl
│   │       ├── card_model.pkl
│   │       ├── loan_model.pkl
│   │       ├── offer_model.pkl
│   │       └── scaler.pkl
│   ├── .env                         # DB credentials (never commit)
│   └── requirements.txt
│
├── Frontend/
│   ├── app.py                       # Streamlit application
│   ├── .env                         # AWS + FastAPI credentials (never commit)
│   └── requirements.txt
│
├── Lambda/
│   └── lambda_function.py           # AWS Lambda ETL function
│
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Setup

### Backend `.env`

```env
DB_HOST=shigil-pc.cfei2y0gokv7.ap-south-1.rds.amazonaws.com
DB_NAME=Axis_Bank
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
FASTAPI_URL=http://127.0.0.1:8000
```

### Frontend `.env`

```env
FASTAPI_URL=http://127.0.0.1:8000
S3_BUCKET=bank-statement-upload-shigil
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

> ⚠️ No spaces around `=` in `.env` files. Add both `.env` files to `.gitignore`.

### `.gitignore`

```
.env
__pycache__/
*.pyc
*.pkl
.DS_Store
```

---

## 🚀 Quick Start

### 1 — Clone & Install

```bash
git clone https://github.com/your-username/axis-bank-intelligence.git

cd Backend
pip install -r requirements.txt

cd ../Frontend
pip install -r requirements.txt
```

### 2 — Configure `.env` Files

Fill in `Backend/.env` and `Frontend/.env` with your credentials.

### 3 — Start FastAPI (Terminal 1)

```bash
cd Backend
uvicorn app.main:app --reload
```

### 4 — Start Streamlit (Terminal 2)

```bash
cd Frontend
streamlit run app.py
```

### 5 — Use the App

1. Open **http://localhost:8501**
2. Click **Get Started** → **Upload Your Statement**
3. Upload an Axis Bank PDF **or** enter an Account ID manually
4. Explore all 5 dashboard tabs

---

## 🔧 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Old PDF data shows on new upload | Session state not cleared | Use `clear_session()` before `load_and_go()` |
| Wrong account loaded after upload | Polling picks oldest JSON | Use `upload_time` filter in `poll_for_account_id()` |
| `NoSuchBucket` on S3 upload | Spaces in `.env` around `=` | Use `S3_BUCKET=name` (no spaces) |
| AWS credentials not found | `.env` missing from `Frontend/` | `cp Backend/.env Frontend/.env` |
| Lambda polling timeout | Lambda slow / not triggered | Use manual Account ID entry |
| FastAPI 422 error | Wrong request format | POST with `{"account_id": "..."}` |
| Blank dashboard | FastAPI not running | Start `uvicorn` in separate terminal first |
| `ModuleNotFoundError` | Dependencies not installed | `pip install -r requirements.txt` |
| DB connection refused | Wrong host / VPC rules | Check `DB_HOST` in `.env` and RDS inbound rules |

---

## 📦 Dependencies

### Backend
```
fastapi>=0.104
uvicorn>=0.24
psycopg2-binary>=2.9
scikit-learn>=1.3
pandas>=2.0
joblib>=1.3
python-dotenv>=1.0
```

### Frontend
```
streamlit>=1.28
boto3>=1.28
plotly>=5.17
requests>=2.31
pandas>=2.0
python-dotenv>=1.0
```

---

