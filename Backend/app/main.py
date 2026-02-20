from fastapi import FastAPI
from app.api.routes.predict import router as predict_router
from app.models.model_loader import load_models

app = FastAPI()

@app.on_event("startup")
def startup_event():
    load_models()

app.include_router(predict_router)
