import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
# Dev: uses brighthii-creds.json in backend directory
# Staging/Prod: uses default service account credentials on Cloud Run
if not firebase_admin._apps:
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brighthii-creds.json")
    if os.path.exists(creds_path):
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

db = firestore.client()

# Environment-based collection prefix
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


def get_collection_name(name: str) -> str:
    if ENVIRONMENT == "prod":
        return name
    return f"{ENVIRONMENT}_{name}"
