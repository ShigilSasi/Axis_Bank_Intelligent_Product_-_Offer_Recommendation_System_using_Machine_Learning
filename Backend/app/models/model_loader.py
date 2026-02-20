import joblib
import os

models = {}

def load_models():
    # go from app/models → app → Backend
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifacts_path = os.path.join(base_dir, "artifacts")

    try:
        models["card_model"] = joblib.load(os.path.join(artifacts_path, "card_model_rf.joblib"))
        models["churn_model"] = joblib.load(os.path.join(artifacts_path, "churn_model_rf.joblib"))
        models["loan_model"] = joblib.load(os.path.join(artifacts_path, "loan_model_rf.joblib"))
        models["offer_model"] = joblib.load(os.path.join(artifacts_path, "offer_model_rf.joblib"))
        models["kmeans_model"] = joblib.load(os.path.join(artifacts_path, "unsup_kmeans.joblib"))
        models["scaler_model"] = joblib.load(os.path.join(artifacts_path, "unsup_scaler.joblib"))

        print("All models loaded successfully.")

    except Exception as e:
        print("Error loading models:", str(e))
