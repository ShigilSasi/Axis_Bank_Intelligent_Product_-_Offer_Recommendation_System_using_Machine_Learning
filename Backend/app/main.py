from fastapi import FastAPI

app = FastAPI(
    title="Axis Bank Intelligent Product & Offer Recommendation System"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to Axis Bank Intelligent Product & Offer Recommendation System"
    }
