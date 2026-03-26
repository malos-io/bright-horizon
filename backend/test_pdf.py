"""Quick test: generate a filled TESDA V2021 PDF overlay.
Run:  python3 backend/test_pdf.py
Open:  backend/test_output.pdf
"""
import sys, os, io, importlib, types
from pathlib import Path
from unittest.mock import MagicMock

# Stub out modules that need auth/firebase so we can import pdf_router cleanly
sys.modules["reusable_components"] = types.ModuleType("reusable_components")
sys.modules["reusable_components.auth"] = MagicMock()
sys.modules["reusable_components.firebase"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()

sys.path.insert(0, os.path.dirname(__file__))
from routers.pdf_router import build_tesda_pdf

sample = {
    "lastName": "Dela Cruz",
    "extensionName": "Jr.",
    "firstName": "Juan",
    "middleName": "Santos",
    "street": "123 Rizal St.",
    "barangay": "San Antonio",
    "district": "District 1",
    "city": "Zamboanga City",
    "province": "Zamboanga del Sur",
    "region": "Region IX (Zamboanga Peninsula)",
    "email": "juan@example.com",
    "facebookAccount": "juan.delacruz",
    "contactNo": "09171234567",
    "nationality": "Filipino",
    "sex": "Female",
    "civilStatus": "Common Law/Live-in",
    "employmentStatus": "Unemployed",
    "employmentType": "Temporary",
    "birthMonth": "March",
    "birthDay": "15",
    "birthYear": "1998",
    "age": "28",
    "birthplaceCity": "Zamboanga City",
    "birthplaceProvince": "Zamboanga del Sur",
    "birthplaceRegion": "Region IX",
    "educationalAttainment": "Doctorate",
    "parentGuardianName": "Maria Dela Cruz",
    "parentGuardianAddress": "123 Rizal St., San Antonio, Zamboanga City",
    "learnerClassification": [
        "4Ps Beneficiary",
        "Agrarian Reform Beneficiary",
        "Balik Probinsya",
        "Displaced Workers",
        "Drug Dependents Surrenderees/Surrenderers",
        "Family Members of AFP and PNP Killed-in-Action",
        "Family Members of AFP and PNP Wounded-in-Action",
        "Farmers and Fishermen",
        "Indigenous People & Cultural Communities",
        "Industry Workers",
        "Inmates and Detainees",
        "MILF Beneficiary",
        "Out-of-School-Youth",
        "Overseas Filipino Workers (OFW) Dependent",
        "RCEF-RESP",
        "Rebel Returnees/Decommissioned Combatants",
        "Returning/Repatriated Overseas Filipino Workers (OFW)",
        "Student",
        "TESDA Alumni",
        "TVET Trainers",
        "Uniformed Personnel",
        "Victim of Natural Disasters and Calamities",
        "Wounded-in-Action AFP & PNP Personnel",
        "Others",
    ],
    "classificationOther": "Solo Parent",
    "course": "Bookkeeping NC III",
    "privacyConsent": "Disagree",
    "scholarshipPackage": "TWSP",
}

buf = build_tesda_pdf(sample)
out = os.path.join(os.path.dirname(__file__), "test_output.pdf")
with open(out, "wb") as f:
    f.write(buf.getvalue())
print(f"Done → {out}")
