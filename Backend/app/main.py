from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes.predict import router as predict_router
from app.models.model_loader import load_models

load_dotenv()

app = FastAPI(title="Axis Bank ML System")

@app.on_event("startup")
def startup_event():
    load_models()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(predict_router)