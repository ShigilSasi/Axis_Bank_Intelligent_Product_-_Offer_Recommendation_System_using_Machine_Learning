import streamlit as st
import requests
import boto3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ================================================================
# CONFIG
# ================================================================
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")
S3_BUCKET   = os.getenv("S3_BUCKET", "your-axis-bank-bucket")
AWS_REGION  = os.getenv("AWS_REGION", "ap-south-1")

AXIS_RED    = "#97144D"
AXIS_DARK   = "#6B0F35"
AXIS_LIGHT  = "#F9E8EF"
AXIS_GOLD   = "#E8A020"
AXIS_TEXT   = "#1A1A2E"

# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(
    page_title="Axis Bank — Smart Banking Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================================
# GLOBAL CSS
# ================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body {{
    font-family: 'DM Sans', sans-serif;
    color: #1A1A2E ;
}}
    .stApp {{ background: #FAFAFA; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}

    .navbar {{
        background: {AXIS_RED};
        padding: 14px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -1rem -1rem 0 -1rem;
        box-shadow: 0 2px 20px rgba(151,20,77,0.3);
    }}
    .navbar-brand {{
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: white;
    }}
    .navbar-tagline {{
        font-size: 0.72rem;
        color: rgba(255,255,255,0.7);
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .hero {{
        background: linear-gradient(135deg, {AXIS_RED} 0%, {AXIS_DARK} 60%, #2D0A1F 100%);
        padding: 80px 60px;
        border-radius: 0 0 40px 40px;
        margin: 0 -1rem 3rem -1rem;
        position: relative;
        overflow: hidden;
    }}
    .hero::before {{
        content: '';
        position: absolute;
        top: -50%; right: -10%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(232,160,32,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .hero-badge {{
        display: inline-block;
        background: rgba(232,160,32,0.2);
        border: 1px solid {AXIS_GOLD};
        color: {AXIS_GOLD};
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.75rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }}
    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        color: white;
        line-height: 1.2;
        margin-bottom: 1rem;
    }}
    .hero-subtitle {{
        font-size: 1.05rem;
        color: rgba(255,255,255,0.78);
        max-width: 520px;
        line-height: 1.7;
    }}

    .metric-card {{
        background: white;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 2px 20px rgba(0,0,0,0.06);
        border-left: 4px solid {AXIS_RED};
        transition: transform 0.2s;
        margin-bottom: 1rem;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(151,20,77,0.12);
    }}
    .metric-label {{
        font-size: 0.72rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-family: 'Playfair Display', serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: {AXIS_TEXT};
    }}

    .section-header {{
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: {AXIS_TEXT};
        margin: 2rem 0 1.2rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 3px solid {AXIS_RED};
        display: inline-block;
    }}

    .account-card {{
        background: linear-gradient(135deg, {AXIS_RED}, {AXIS_DARK});
        border-radius: 20px;
        padding: 28px;
        color: white;
    }}

    .rec-card {{
        background: white;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.06);
        border-top: 4px solid {AXIS_RED};
        transition: all 0.3s;
        margin-bottom: 1rem;
    }}
    .rec-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 35px rgba(151,20,77,0.14);
    }}

    .badge-eligible {{
        background: #E8F5E9; color: #2E7D32;
        padding: 8px 18px; border-radius: 20px;
        font-weight: 600; font-size: 0.82rem;
        display: inline-block; border: 1px solid #A5D6A7;
    }}
    .badge-not-eligible {{
        background: #FFEBEE; color: #C62828;
        padding: 8px 18px; border-radius: 20px;
        font-weight: 600; font-size: 0.82rem;
        display: inline-block; border: 1px solid #FFCDD2;
    }}

    .cluster-card {{
        background: linear-gradient(135deg, #1A1A2E, #16213E);
        border-radius: 20px;
        padding: 28px;
        color: white;
        text-align: center;
    }}

    .axis-divider {{
        height: 3px;
        background: linear-gradient(90deg, {AXIS_RED}, {AXIS_GOLD}, transparent);
        border-radius: 2px;
        margin: 1.5rem 0;
    }}

    .step-box {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}

    .manual-entry-box {{
        background: white;
        border: 1px solid #eee;
        border-radius: 16px;
        padding: 28px;
        margin-top: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }}

    .stButton > button {{
        background: {AXIS_RED} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: {AXIS_DARK} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(151,20,77,0.3) !important;
    }}
    .stFileUploader > div {{
        border: 2px dashed {AXIS_RED} !important;
        border-radius: 16px !important;
        background: {AXIS_LIGHT} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ================================================================
# HELPERS
# ================================================================
def navbar():
    st.markdown("""
    <div class="navbar">
        <div>
            <div class="navbar-brand">🏦 Axis Bank</div>
        </div>
        <div style="color:rgba(255,255,255,0.7);font-size:0.82rem;">
            Smart Banking Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)


def fmt_inr(val):
    try:
        val = float(val)
        if val >= 1_00_000:
            return f"₹{val/1_00_000:.2f}L"
        elif val >= 1000:
            return f"₹{val/1000:.1f}K"
        return f"₹{val:,.0f}"
    except Exception:
        return "₹0"


def upload_to_s3(file_bytes, filename):
    try:
        s3  = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        key = f"uploads/{filename}"
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=file_bytes, ContentType="application/pdf")
        return True
    except Exception as e:
        st.error(f"S3 upload failed: {e}")
        return False


def poll_for_account_id(filename, retries=20, delay=3):
    """
    Poll S3 processed/ for the JSON that belongs to this specific uploaded file.
    Matches by looking for JSONs created AFTER upload started.
    """
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    upload_time = time.time()  # Record when this upload started

    for _ in range(retries):
        try:
            res = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="processed/")
            contents = res.get("Contents", [])

            # Only consider JSON files created AFTER this upload started
            new_jsons = [
                o for o in contents
                if o["Key"].endswith("_account_info.json")
                and o["LastModified"].timestamp() >= upload_time - 5
            ]

            if new_jsons:
                # Pick the most recently modified one
                latest = sorted(new_jsons, key=lambda x: x["LastModified"], reverse=True)[0]
                obj    = s3.get_object(Bucket=S3_BUCKET, Key=latest["Key"])
                info   = json.loads(obj["Body"].read())
                acct   = info.get("account_number")
                if acct:
                    return acct
        except Exception:
            pass
        time.sleep(delay)
    return None


def call_predict(account_id):
    try:
        r = requests.post(f"{FASTAPI_URL}/predict/",
                          json={"account_id": account_id}, timeout=30)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def call_transactions(account_id):
    try:
        r = requests.get(f"{FASTAPI_URL}/predict/transactions/{account_id}", timeout=30)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def call_account(account_id):
    try:
        r = requests.get(f"{FASTAPI_URL}/predict/account/{account_id}", timeout=30)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def clear_session():
    """Clear all old data from session state."""
    st.session_state.predictions  = None
    st.session_state.transactions = None
    st.session_state.account_info = None
    st.session_state.account_id   = None
    st.session_state.active_tab   = "overview"


def load_and_go(account_id):
    """Clear old data, fetch fresh data, navigate to dashboard."""
    account_id = account_id.strip()

    # ✅ Clear old data first — previous PDF never bleeds into new one
    st.session_state.predictions  = None
    st.session_state.transactions = None
    st.session_state.account_info = None
    st.session_state.active_tab   = "overview"

    # ✅ Load fresh data for new account
    st.session_state.account_id   = account_id
    st.session_state.predictions  = call_predict(account_id)
    st.session_state.transactions = call_transactions(account_id)
    st.session_state.account_info = call_account(account_id)
    st.session_state.page         = "dashboard"


# ================================================================
# CHART HELPERS
# ================================================================
BASE_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="DM Sans", color=AXIS_TEXT),
    margin=dict(t=70, b=60, l=60, r=40),
    xaxis=dict(
        title_font=dict(size=14, color=AXIS_TEXT),
        tickfont=dict(size=12, color=AXIS_TEXT)
    ),
    yaxis=dict(
        title_font=dict(size=14, color=AXIS_TEXT),
        tickfont=dict(size=12, color=AXIS_TEXT)
    )
)
COLORS = [AXIS_RED, AXIS_GOLD, "#E8726A", "#2196F3",
          "#4CAF50", "#9C27B0", "#FF9800", "#00BCD4", "#795548", "#607D8B"]


def pie_spending(df):
    d = df[df["debit"] > 0].groupby("category")["debit"].sum().reset_index()
    d = d.sort_values("debit", ascending=False).head(10)
    fig = px.pie(d, values="debit", names="category",
                 color_discrete_sequence=COLORS, hole=0.4,
                 title="Spending by Category")
    fig.update_layout(**BASE_LAYOUT)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def bar_monthly(df):
    df = df.copy()
    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df["month"]    = df["txn_date"].dt.to_period("M").astype(str)
    m  = df.groupby("month").agg(credit=("credit","sum"), debit=("debit","sum")).reset_index()
    fig = go.Figure([
        go.Bar(x=m["month"], y=m["credit"], name="Credit",
               marker_color="#4CAF50", opacity=0.85),
        go.Bar(x=m["month"], y=m["debit"],  name="Debit",
               marker_color=AXIS_RED, opacity=0.85),
    ])
    fig.update_layout(**BASE_LAYOUT, title="Monthly Credit vs Debit",
                      barmode="group", xaxis_title="Month", yaxis_title="₹")
    return fig


def line_balance(df):
    df = df.copy()
    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df = df.sort_values("txn_date")
    fig = go.Figure(go.Scatter(
        x=df["txn_date"], y=df["balance"], mode="lines",
        line=dict(color=AXIS_RED, width=2),
        fill="tozeroy", fillcolor="rgba(151,20,77,0.07)"
    ))
    fig.update_layout(**BASE_LAYOUT, title="Daily Balance Trend",
                      xaxis_title="Date", yaxis_title="Balance (₹)")
    return fig


def bar_merchants(df):
    d = df[df["debit"] > 0].groupby("merchant")["debit"].sum().reset_index()
    d = d.sort_values("debit", ascending=True).tail(10)
    fig = go.Figure(go.Bar(
        x=d["debit"], y=d["merchant"], orientation="h",
        marker_color=AXIS_RED,
        text=[fmt_inr(v) for v in d["debit"]], textposition="outside"
    ))
    fig.update_layout(**BASE_LAYOUT, title="Top 10 Merchants by Spend")
    return fig


def bar_spend_dist(feats):
    cats = ["Food", "Shopping", "Transport", "Rent", "EMI", "Utility"]
    vals = [feats.get("food_spend", 0), feats.get("shopping_spend", 0),
            feats.get("transport_spend", 0), feats.get("rent_spend", 0),
            feats.get("emi_spend", 0), feats.get("utility_spend", 0)]
    fig = go.Figure(go.Bar(
        x=cats, y=vals, marker_color=COLORS[:6],
        text=[fmt_inr(v) for v in vals], textposition="outside"
    ))
    fig.update_layout(**BASE_LAYOUT, title="Spend Distribution by Category",
                      xaxis_title="Category", yaxis_title="₹")
    return fig


def donut_channel(feats):
    fig = go.Figure(go.Pie(
        labels=["UPI", "POS / CARD", "NEFT"],
        values=[feats.get("upi_txn", 0), feats.get("pos_txn", 0), feats.get("neft_txn", 0)],
        hole=0.5,
        marker_colors=[AXIS_RED, AXIS_GOLD, "#2196F3"]
    ))
    fig.update_layout(**BASE_LAYOUT, title="Channel Usage")
    return fig


def bar_ratios(feats):
    labels = ["Savings Ratio", "EMI Ratio", "Food Ratio", "Digital Ratio"]
    vals   = [feats.get("savings_ratio", 0), feats.get("emi_ratio", 0),
              feats.get("food_ratio", 0), feats.get("digital_ratio", 0)]
    fig = go.Figure(go.Bar(
        x=labels, y=vals, marker_color=[AXIS_RED, AXIS_GOLD, "#4CAF50", "#2196F3"],
        text=[f"{v:.3f}" for v in vals], textposition="outside"
    ))
    fig.update_layout(**BASE_LAYOUT, title="Behavioural Ratios")
    return fig


def heatmap_category(df):
    df = df.copy()
    df["txn_date"] = pd.to_datetime(df["txn_date"])
    df["month"]    = df["txn_date"].dt.to_period("M").astype(str)
    pivot = df[df["debit"] > 0].pivot_table(
        values="debit", index="category", columns="month",
        aggfunc="sum", fill_value=0
    )
    fig = px.imshow(
        pivot, aspect="auto",
        color_continuous_scale=[[0, "white"], [0.5, AXIS_LIGHT], [1, AXIS_RED]],
        title="Category-wise Spend Heatmap by Month"
    )
    fig.update_layout(**BASE_LAYOUT)
    return fig


def gauge_churn(prob):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        number={"suffix": "%"},
        title={"text": "Churn Risk", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar":  {"color": AXIS_RED},
            "steps": [
                {"range": [0, 30],   "color": "#E8F5E9"},
                {"range": [30, 60],  "color": "#FFF9C4"},
                {"range": [60, 100], "color": "#FFEBEE"},
            ],
        }
    ))
    fig.update_layout(paper_bgcolor="white", font=dict(family="DM Sans"),
                      height=260, margin=dict(t=60, b=10, l=20, r=20))
    return fig


# ================================================================
# SESSION STATE
# ================================================================
for key, default in [
    ("page", "welcome"), ("account_id", None),
    ("predictions", None), ("transactions", None),
    ("account_info", None), ("active_tab", "overview")
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ================================================================
# PAGE: WELCOME
# ================================================================
def page_welcome():
    navbar()

    st.markdown(f"""
    <div class="hero">
        <div class="hero-badge">✦ Powered by Machine Learning</div>
        <div class="hero-title">Welcome to<br>Axis Bank<br>Intelligence</div>
        <div class="hero-subtitle">
            Upload your bank statement and get instant insights —
            personalized recommendations, spending analysis, and
            AI-powered financial intelligence tailored for you.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("📊", "Smart Analytics",     "Deep dive into your spending patterns"),
        ("🤖", "AI Predictions",      "ML-powered churn risk & eligibility"),
        ("🎯", "Personalized Offers", "Tailored cards, loans & exclusive offers"),
        ("🔒", "Secure & Private",    "Bank-grade encryption, always"),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
        with col:
            st.markdown(f"""
            <div class="step-box">
                <div style="font-size:2rem;margin-bottom:10px;">{icon}</div>
                <div style="font-weight:600;font-size:0.92rem;margin-bottom:6px;">{title}</div>
                <div style="font-size:0.78rem;color:#888;line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("🚀 Get Started"):
            st.session_state.page = "upload"
            st.rerun()

    st.markdown("<div class='axis-divider'></div>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    for col, val, lbl in zip([s1, s2, s3, s4],
                              ["1000+", "6", "4", "99.9%"],
                              ["Customers Analyzed", "ML Models", "Segments", "Accuracy"]):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:18px;">
                <div style="font-family:'Playfair Display',serif;font-size:2rem;
                     font-weight:700;color:{AXIS_RED};">{val}</div>
                <div style="font-size:0.75rem;color:#888;text-transform:uppercase;
                     letter-spacing:1px;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# PAGE: UPLOAD
# ================================================================
def page_upload():
    navbar()
    st.markdown("<br>", unsafe_allow_html=True)

    col_back, _ = st.columns([1, 6])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown("<div class='section-header'>Upload Your Statement</div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown(f"""
        <div style="background:white;border:2px dashed {AXIS_RED};border-radius:20px;
             padding:40px;text-align:center;margin-bottom:1rem;">
            <div style="font-size:3rem;margin-bottom:0.8rem;">📄</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.15rem;
                 font-weight:600;margin-bottom:0.4rem;">Drop your PDF here</div>
            <div style="font-size:0.82rem;color:#888;">Axis Bank statement PDFs only</div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("Choose PDF", type=["pdf"],
                                    label_visibility="collapsed")

        if uploaded:
            st.markdown(f"""
            <div style="background:{AXIS_LIGHT};border-radius:12px;padding:14px;
                 border-left:4px solid {AXIS_RED};margin-bottom:1rem;">
                <div style="font-weight:600;">📎 {uploaded.name}</div>
                <div style="font-size:0.78rem;color:#888;">{uploaded.size/1024:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Analyze My Statement"):
                progress = st.progress(0, text="Uploading to S3...")
                success  = upload_to_s3(uploaded.read(), uploaded.name)
                progress.progress(30, text="Waiting for Lambda to process...")

                if success:
                    account_id = poll_for_account_id(uploaded.name)
                    progress.progress(70, text="Fetching ML predictions...")

                    if account_id:
                        load_and_go(account_id)
                        progress.progress(100, text="Done!")
                        st.success(f"✅ Analysis complete — Account {account_id}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("⚠️ Processing timed out. Use manual entry below.")
                else:
                    st.error("S3 upload failed. Check configuration.")

        # ---- MANUAL ENTRY ----
        st.markdown(f"""
        <div class="manual-entry-box">
            <div style="font-family:'Playfair Display',serif;font-size:1rem;
                 font-weight:600;color:{AXIS_TEXT};margin-bottom:6px;">
                Already processed? Enter Account ID
            </div>
            <div style="font-size:0.8rem;color:#888;margin-bottom:14px;">
                If your PDF was already uploaded and processed, enter your account ID directly.
            </div>
        </div>
        """, unsafe_allow_html=True)

        manual_id = st.text_input(
            "Account ID",
            placeholder="e.g. 920000000001",
            key="manual_account_id"
        )

        if st.button("🔍 Load Dashboard", key="manual_go"):
            if manual_id.strip():
                with st.spinner("Loading your data..."):
                    load_and_go(manual_id.strip())
                st.rerun()
            else:
                st.error("Please enter a valid Account ID")

    with right:
        st.markdown(f"""
        <div style="background:white;border-radius:18px;padding:28px;
             box-shadow:0 4px 20px rgba(0,0,0,0.06);">
            <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                 font-weight:600;margin-bottom:1.5rem;">How it works</div>
        """, unsafe_allow_html=True)

        for num, title, desc in [
            ("1", "Upload PDF",    "Securely upload your Axis Bank statement"),
            ("2", "AI Extraction", "Lambda extracts all transactions automatically"),
            ("3", "ML Analysis",   "6 models analyze your financial behavior"),
            ("4", "Get Insights",  "Dashboard + personalized recommendations"),
        ]:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;margin-bottom:18px;">
                <div style="min-width:30px;height:30px;background:{AXIS_RED};color:white;
                     border-radius:50%;display:flex;align-items:center;justify-content:center;
                     font-weight:700;font-size:0.82rem;margin-right:12px;margin-top:2px;">{num}</div>
                <div>
                    <div style="font-weight:600;font-size:0.88rem;">{title}</div>
                    <div style="font-size:0.78rem;color:#888;margin-top:2px;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:{AXIS_LIGHT};border-radius:14px;padding:18px;
             margin-top:1.2rem;border:1px solid rgba(151,20,77,0.15);">
            <div style="font-weight:600;color:{AXIS_RED};margin-bottom:6px;">🔒 Bank-Grade Security</div>
            <div style="font-size:0.8rem;color:#666;line-height:1.6;">
                Your data is encrypted in transit and at rest.
                We never share your financial information with third parties.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# PAGE: DASHBOARD
# ================================================================
def page_dashboard():
    navbar()

    account_id   = st.session_state.account_id
    predictions  = st.session_state.predictions
    transactions = st.session_state.transactions
    account_info = st.session_state.account_info

    if not account_id or not predictions:
        st.warning("No data found. Please upload a statement or enter an Account ID.")
        if st.button("Go to Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
    if not df.empty:
        df["debit"]  = pd.to_numeric(df["debit"],  errors="coerce").fillna(0)
        df["credit"] = pd.to_numeric(df["credit"], errors="coerce").fillna(0)
        df["balance"]= pd.to_numeric(df["balance"],errors="coerce").fillna(0)

    # ---- Tab navigation ----
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2, t3, t4, t5, t6 = st.columns(6)
    tabs = [
        (t1, "🏠 Overview",        "overview"),
        (t2, "📊 Transactions",    "transactions"),
        (t3, "🔬 Features",        "features"),
        (t4, "🤖 ML Insights",     "ml"),
        (t5, "🎯 Recommendations", "recommendations"),
        (t6, "⬅ New Statement",    "upload"),
    ]
    for col, label, key in tabs:
        with col:
            if st.button(label, key=f"nav_{key}"):
                if key == "upload":
                    # ✅ Clear all data when going back to upload new statement
                    clear_session()
                    st.session_state.page = "upload"
                else:
                    st.session_state.active_tab = key
                st.rerun()

    st.markdown("<div class='axis-divider'></div>", unsafe_allow_html=True)
    tab = st.session_state.active_tab

    # ============================================================
    # OVERVIEW
    # ============================================================
    if tab == "overview":
        st.markdown("<div class='section-header'>Account Overview</div>", unsafe_allow_html=True)

        name     = (account_info or {}).get("account_holder", "Account Holder")
        branch   = (account_info or {}).get("branch", "N/A")
        period   = (account_info or {}).get("statement_period", "N/A")
        acc_type = (account_info or {}).get("account_type", "Savings Account")
        ifsc     = (account_info or {}).get("ifsc", "N/A")

        card_col, metrics_col = st.columns([1, 1.8])

        with card_col:
            st.markdown(f"""
            <div class="account-card">
                <div style="font-size:0.68rem;color:rgba(255,255,255,0.55);
                     letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">{acc_type}</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.35rem;
                     font-weight:600;margin-bottom:4px;">{name}</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.65);letter-spacing:2px;">
                    •••• •••• •••• {account_id[-4:]}
                </div>
                <div style="margin-top:18px;display:flex;gap:24px;">
                    <div>
                        <div style="font-size:0.65rem;color:rgba(255,255,255,0.45);">BRANCH</div>
                        <div style="font-size:0.82rem;">{branch}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;color:rgba(255,255,255,0.45);">IFSC</div>
                        <div style="font-size:0.82rem;">{ifsc}</div>
                    </div>
                </div>
                <div style="margin-top:12px;">
                    <div style="font-size:0.65rem;color:rgba(255,255,255,0.45);">STATEMENT PERIOD</div>
                    <div style="font-size:0.8rem;color:rgba(255,255,255,0.8);">{period}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with metrics_col:
            total_credit = float(df["credit"].sum()) if not df.empty else 0
            total_debit  = float(df["debit"].sum())  if not df.empty else 0
            total_txns   = len(df)

            r1, r2 = st.columns(2)
            r3, r4 = st.columns(2)
            for col, lbl, val, color in [
                (r1, "💰 Total Credit",  fmt_inr(total_credit),  "#4CAF50"),
                (r2, "💸 Total Debit",   fmt_inr(total_debit),   AXIS_RED),
                (r3, "🔄 Transactions",  f"{total_txns:,}",      "#2196F3"),
                (r4, "👤 Segment",       predictions.get("cluster_label","N/A"), AXIS_GOLD),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color:{color};">
                        <div class="metric-label">{lbl}</div>
                        <div class="metric-value" style="font-size:1.4rem;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ============================================================
    # TRANSACTIONS
    # ============================================================
    elif tab == "transactions":
        st.markdown("<div class='section-header'>Transaction Dashboard</div>", unsafe_allow_html=True)

        if df.empty:
            st.info("No transaction data available.")
            return

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(pie_spending(df), use_container_width=True)
        with c2:
            st.plotly_chart(bar_monthly(df), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(line_balance(df), use_container_width=True)
        with c4:
            st.plotly_chart(bar_merchants(df), use_container_width=True)

        st.markdown("<div class='section-header'>Transaction History</div>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1:
            cats  = ["All"] + sorted(df["category"].unique().tolist())
            cat_f = st.selectbox("Category", cats)
        with f2:
            chs   = ["All"] + sorted(df["channel"].unique().tolist())
            ch_f  = st.selectbox("Channel", chs)
        with f3:
            typ_f = st.selectbox("Type", ["All", "Debit", "Credit"])

        fdf = df.copy()
        if cat_f != "All": fdf = fdf[fdf["category"] == cat_f]
        if ch_f  != "All": fdf = fdf[fdf["channel"]  == ch_f]
        if typ_f == "Debit":  fdf = fdf[fdf["debit"]  > 0]
        if typ_f == "Credit": fdf = fdf[fdf["credit"] > 0]

        show_cols = [c for c in ["txn_date","narration","merchant","category",
                                  "channel","debit","credit","balance"] if c in fdf.columns]
        st.dataframe(fdf[show_cols].rename(columns={
            "txn_date":"Date","narration":"Narration","merchant":"Merchant",
            "category":"Category","channel":"Channel",
            "debit":"Debit (₹)","credit":"Credit (₹)","balance":"Balance (₹)"
        }), use_container_width=True, height=420)

    # ============================================================
    # FEATURES
    # ============================================================
    elif tab == "features":
        st.markdown("<div class='section-header'>Customer Behavioral Analysis</div>",
            unsafe_allow_html=True)

        if df.empty:
            st.info("No data available.")
            return

        td = float(df["debit"].sum())
        tc = float(df["credit"].sum())
        tt = len(df)

        feats = {
            "food_spend":      float(df[df["category"]=="Food & Dining"]["debit"].sum()),
            "shopping_spend":  float(df[df["category"]=="Shopping"]["debit"].sum()),
            "transport_spend": float(df[df["category"]=="Transport"]["debit"].sum()),
            "rent_spend":      float(df[df["category"]=="Rent"]["debit"].sum()),
            "emi_spend":       float(df[df["category"]=="Loan EMI"]["debit"].sum()),
            "utility_spend":   float(df[df["category"]=="Utilities"]["debit"].sum()),
            "upi_txn":         int((df["channel"]=="UPI").sum()),
            "pos_txn":         int((df["channel"]=="POS / CARD").sum()),
            "neft_txn":        int((df["channel"]=="NEFT").sum()),
            "savings_ratio":   tc / (td + 1),
            "emi_ratio":       float(df[df["category"]=="Loan EMI"]["debit"].sum()) / (tc + 1),
            "food_ratio":      float(df[df["category"]=="Food & Dining"]["debit"].sum()) / (td + 1),
            "digital_ratio":   (int((df["channel"]=="UPI").sum()) +
                                int((df["channel"]=="POS / CARD").sum())) / (tt + 1),
        }

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(bar_spend_dist(feats), use_container_width=True)
        with c2:
            st.plotly_chart(donut_channel(feats), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(bar_ratios(feats), use_container_width=True)
        with c4:
            st.plotly_chart(heatmap_category(df), use_container_width=True)

        st.markdown("<div class='section-header'>Feature Summary Table</div>",
                    unsafe_allow_html=True)
        feat_df = pd.DataFrame([
            {"Feature": k.replace("_"," ").title(),
             "Value": f"{v:.4f}" if isinstance(v, float) else str(v)}
            for k, v in feats.items()
        ])
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

    # ============================================================
    # ML INSIGHTS
    # ============================================================
    elif tab == "ml":
        st.markdown("<div class='section-header'>AI-Powered Customer Intelligence</div>",
            unsafe_allow_html=True)

        cluster_descs = {
            "Affluent Borrowers":         "High income, active borrowers with strong repayment.",
            "Conservative Savers":        "Low spenders with high savings — financially disciplined.",
            "Digital Lifestyle Spenders": "Heavy UPI users with lifestyle-oriented spending.",
            "Stable Mass Market":         "Balanced spending with moderate income.",
        }
        cluster_label = predictions.get("cluster_label", "Unknown")
        churn_prob    = float(predictions.get("churn_probability", 0))

        cl_col, ch_col = st.columns(2)
        with cl_col:
            st.markdown(f"""
            <div class="cluster-card">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);
                     letter-spacing:2px;text-transform:uppercase;">Customer Segment</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.5rem;
                     font-weight:700;color:{AXIS_GOLD};margin:10px 0;">{cluster_label}</div>
                <div style="font-size:0.83rem;color:rgba(255,255,255,0.62);line-height:1.6;">
                    {cluster_descs.get(cluster_label,"")}
                </div>
                <div style="margin-top:20px;background:rgba(255,255,255,0.06);
                     border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:0.68rem;color:rgba(255,255,255,0.4);">CLUSTER ID</div>
                    <div style="font-size:1.6rem;font-weight:700;color:{AXIS_GOLD};">
                        #{predictions.get("cluster",0)}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with ch_col:
            st.plotly_chart(gauge_churn(churn_prob), use_container_width=True)
            risk_level = "🔴 High Risk"   if churn_prob > 0.6 else \
                         "🟡 Medium Risk" if churn_prob > 0.3 else "🟢 Low Risk"
            st.markdown(f"""
            <div style="text-align:center;background:white;border-radius:12px;
                 padding:14px;box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                <div style="font-weight:600;font-size:1rem;">{risk_level}</div>
                <div style="font-size:0.78rem;color:#888;margin-top:4px;">
                    Churn probability: {churn_prob*100:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='axis-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="
            font-family:'Playfair Display',serif;
            font-size:1.3rem;
            font-weight:700;
            margin-bottom:1rem;
            color:{AXIS_TEXT};
            border-bottom:2px solid {AXIS_RED};
            padding-bottom:6px;">
            Product Eligibility & Risk Assessment
        </div>
        """, unsafe_allow_html=True)

        e1, e2, e3, e4 = st.columns(4)
        churn_risk = predictions.get("churn_risk", 0)
        for col, lbl, eligible, inv in [
            (e1, "💳 Credit Card", predictions.get("card_suitable",  0), False),
            (e2, "🏦 Loan",        predictions.get("loan_eligible",  0), False),
            (e3, "🎁 Offers",      predictions.get("offer_eligible", 0), False),
            (e4, "⚠️ Churn Risk",  churn_risk,                           True),
        ]:
            with col:
                is_pos = (not inv and eligible == 1) or (inv and eligible == 0)
                badge  = "badge-eligible" if is_pos else "badge-not-eligible"
                if inv:
                    status = "✅ Low Risk"    if eligible == 0 else "⚠️ High Risk"
                else:
                    status = "✅ Eligible"    if eligible == 1 else "❌ Not Eligible"

                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:22px;
                     text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
                    <div style="
                        font-weight:700;
                        font-size:0.95rem;
                        margin-bottom:12px;
                        color:{AXIS_TEXT};">
                        {lbl}
                    </div>
                    <div class="{badge}">{status}</div>
                </div>
                """, unsafe_allow_html=True)

        if not df.empty:
            st.markdown("<div class='axis-divider'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-family:'Playfair Display',serif;font-size:1.2rem;
                 font-weight:600;margin-bottom:1rem;">You vs Cluster Average</div>
            """, unsafe_allow_html=True)

            td = float(df["debit"].sum())
            tc = float(df["credit"].sum())
            tt = len(df)
            my_savings = tc / (td + 1)
            my_digital = (int((df["channel"]=="UPI").sum()) +
                          int((df["channel"]=="POS / CARD").sum())) / (tt + 1)

            cluster_avgs = {
                "Affluent Borrowers":         {"savings": 1.4, "digital": 0.65},
                "Conservative Savers":        {"savings": 1.8, "digital": 0.45},
                "Digital Lifestyle Spenders": {"savings": 0.9, "digital": 0.82},
                "Stable Mass Market":         {"savings": 1.1, "digital": 0.55},
            }
            avg = cluster_avgs.get(cluster_label, {"savings": 1.0, "digital": 0.5})

            fig = go.Figure([
                go.Bar(name="You", x=["Savings Ratio","Digital Ratio"],
                       y=[round(my_savings,2), round(my_digital,2)],
                       marker_color=AXIS_RED,
                       text=[round(my_savings,2), round(my_digital,2)],
                       textposition="outside"),
                go.Bar(name="Cluster Avg", x=["Savings Ratio","Digital Ratio"],
                       y=[avg["savings"], avg["digital"]],
                       marker_color=AXIS_GOLD,
                       text=[avg["savings"], avg["digital"]],
                       textposition="outside"),
            ])
            fig.update_layout(**BASE_LAYOUT, title="Your Ratios vs Cluster Average",
                              barmode="group")
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # RECOMMENDATIONS
    # ============================================================
    elif tab == "recommendations":
        st.markdown("<div class='section-header'>Personalized Recommendations</div>",
                    unsafe_allow_html=True)

        recs         = predictions.get("recommendations", {})
        credit_cards = recs.get("credit_cards", [])
        loans        = recs.get("loans", [])
        offers       = recs.get("offers", [])

        card_info = {
            "Shopping Rewards Credit Card": ("Up to 5% cashback on all shopping", "Shopping", AXIS_RED),
            "Dining Cashback Card":         ("20% off at 1000+ partner restaurants","Dining",  "#E91E63"),
            "Fuel Benefits Card":           ("Save ₹2000/month on fuel spends",    "Fuel",    "#FF9800"),
            "Digital Cashback Card":        ("1% cashback on all UPI transactions", "Digital", "#2196F3"),
            "Secured Credit Card":          ("Guaranteed approval, build credit",   "Entry",   "#9C27B0"),
        }
        loan_info = {
            "Pre-approved Personal Loan": ("Up to ₹25L | Instant disbursal",   "Pre-Approved", AXIS_GOLD),
            "Instant Personal Loan":      ("Up to ₹10L | No documents needed", "Instant",      "#FF9800"),
            "Short-term Digital Loan":    ("₹50K–₹5L | 100% online process",   "Digital",      "#2196F3"),
            "Top-up Loan":                ("Add funds to your existing loan",   "Top-up",       "#4CAF50"),
        }
        offer_info = {
            "UPI Cashback Offer":     ("₹50 cashback on 10 UPI transactions", "UPI",      "#4CAF50"),
            "Shopping Cashback Offer":("10% cashback up to ₹500 on shopping", "Shopping", "#E91E63"),
            "Utility Cashback Offer": ("5% cashback on electricity bills",     "Utility",  "#FF9800"),
            "Dining Discount Offer":  ("Flat 25% off at 500+ restaurants",     "Dining",   "#9C27B0"),
        }

        def render_cards(items, info_map, btn_label):
            if not items:
                return
            cols = st.columns(min(len(items), 3))
            for i, item in enumerate(items):
                desc, tag, color = info_map.get(item, ("Exclusive benefits","Special", AXIS_RED))
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="rec-card" style="border-top-color:{color};">
                        <div style="display:inline-block;background:rgba(0,0,0,0.05);
                             color:{color};padding:4px 12px;border-radius:20px;
                             font-size:0.7rem;font-weight:600;letter-spacing:1px;
                             text-transform:uppercase;margin-bottom:12px;">{tag}</div>
                        <div style="font-family:'Playfair Display',serif;font-size:0.98rem;
                             font-weight:600;margin-bottom:8px;color:{AXIS_TEXT};">{item}</div>
                        <div style="font-size:0.8rem;color:#777;margin-bottom:18px;
                             line-height:1.5;">{desc}</div>
                        <div style="background:{color};color:white;padding:10px;
                             border-radius:8px;text-align:center;font-weight:600;
                             font-size:0.83rem;">{btn_label} →</div>
                    </div>
                    """, unsafe_allow_html=True)

        if credit_cards:
            st.markdown(f"""
            <div style="font-family:'Playfair Display',serif;font-size:1.15rem;
                 font-weight:600;margin:1.5rem 0 1rem;">💳 Recommended Credit Cards</div>
            """, unsafe_allow_html=True)
            render_cards(credit_cards, card_info, "Apply Now")

        if loans:
            st.markdown(f"""
            <div style="font-family:'Playfair Display',serif;font-size:1.15rem;
                 font-weight:600;margin:2rem 0 1rem;">🏦 Loan Offers</div>
            """, unsafe_allow_html=True)
            render_cards(loans, loan_info, "Check Eligibility")

        if offers:
            st.markdown(f"""
            <div style="font-family:'Playfair Display',serif;font-size:1.15rem;
                 font-weight:600;margin:2rem 0 1rem;">🎁 Exclusive Offers</div>
            """, unsafe_allow_html=True)
            render_cards(offers, offer_info, "Activate Offer")

        if not credit_cards and not loans and not offers:
            st.markdown(f"""
            <div style="text-align:center;padding:60px;background:white;
                 border-radius:20px;box-shadow:0 2px 15px rgba(0,0,0,0.05);">
                <div style="font-size:3rem;margin-bottom:1rem;">🎯</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.2rem;
                     font-weight:600;margin-bottom:0.5rem;">No recommendations yet</div>
                <div style="font-size:0.83rem;color:#888;">
                    Your profile doesn't match current criteria.
                    Check back after more transactions.
                </div>
            </div>
            """, unsafe_allow_html=False)


# ================================================================
# ROUTER
# ================================================================
if st.session_state.page == "welcome":
    page_welcome()
elif st.session_state.page == "upload":
    page_upload()
elif st.session_state.page == "dashboard":
    page_dashboard()