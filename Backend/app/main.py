from fastapi import FastAPI
from app.model_loader import load_models

app = FastAPI(title="Axis Bank Intelligent Product & Offer Recommendation System")

@app.on_event("startup")
def startup_event():
    load_models()

@app.get("/")
def home():
    return {"message": "API is running successfully"}
