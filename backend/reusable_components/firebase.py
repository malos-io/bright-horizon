import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
# Dev: uses local emulators with emulator credentials
# Staging/Prod: uses default service account on Cloud Run
if not firebase_admin._apps:
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        # Dev mode: use emulator credentials
        emulator_creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "emulator-creds.json")
        cred = credentials.Certificate(emulator_creds_path)
        firebase_admin.initialize_app(cred)
    else:
        # Staging/Prod (Cloud Run): use default service account
        firebase_admin.initialize_app()

db = firestore.client()
