## Axis Bank Intelligent Product & Offer Recommendation System
# AI-Powered Smart Banking Intelligence Platform

A full-stack Machine Learning system that analyzes customer bank statements, extracts behavioral features, performs segmentation & churn prediction, and delivers personalized banking product recommendations.

Built using:

 - Machine Learning (Scikit-Learn / XGBoost)

 - AWS (S3, Lambda, RDS)

 - PostgreSQL

 - FastAPI

 - Streamlit

 - Plotly

# Project Overview

This system enables:

 - Automated PDF bank statement ingestion

 - Transaction extraction using AWS Lambda

 - Feature engineering from financial behavior

 - Customer segmentation (Clustering)

 - Churn prediction

 - Product eligibility scoring

 - Personalized recommendations

 - Interactive dashboard visualization

# System Architecture
 - User Upload (Streamlit)
        ↓
 - AWS S3 (Raw PDF Storage)
        ↓
 - AWS Lambda (PDF Parsing & Transaction Extraction)
        ↓
 - PostgreSQL (RDS)
        ↓
 - FastAPI (ML Inference Layer)
        ↓
 - Streamlit Dashboard (Visualization)
