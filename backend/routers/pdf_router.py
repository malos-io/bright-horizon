import io
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

from reusable_components.auth import verify_jwt
from reusable_components.firebase import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["pdf"])

# Path to the TESDA MIS 03-01 (ver. 2021) form template
TEMPLATE_PATH = Path(__file__).parent.parent / "tesda_files" / "REGISTRATION FORM V2021.pdf"

FONT = "Helvetica-Bold"
FONT_SIZE = 9
SMALL_SIZE = 7

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _compute_age(data: dict) -> str:
    """Compute age from birthMonth, birthDay, birthYear fields."""
    month_str = data.get("birthMonth", "")
    day_str = data.get("birthDay", "")
    year_str = data.get("birthYear", "")
    if not month_str or not day_str or not year_str:
        return ""
    try:
        m = MONTHS.index(month_str)
        d = int(day_str)
        y = int(year_str)
    except (ValueError, IndexError):
        return ""
    today = datetime.now().date()
    age = today.year - y
    if (today.month, today.day) < (m + 1, d):
        age -= 1
    return str(age) if age >= 0 else ""


def _v(data: dict, key: str, default: str = "") -> str:
    val = data.get(key, default)
    return str(val) if val else default


def _short_region(value: str) -> str:
    """Extract short region name, e.g. 'Region IX (Zamboanga Peninsula)' -> 'Region IX'."""
    if "(" in value:
        return value.split("(")[0].strip()
    return value


# Backward-compat: map old form option values → V2021 option values
_EDUC_MAP = {
    "No Grade Completed / Pre-School (Nursery/Kinder/Prep)": "No Grade Completed",
    "Elementary Level": "Elementary Undergraduate",
    "High School Level": "High School Undergraduate",
    "College Level": "College Undergraduate",
    "College Graduate or Higher": "College Graduate",
    "Post-Secondary Level/Graduate": "Post-Secondary Non-Tertiary/Technical Vocational Course Graduate",
}

_EMPLOYMENT_MAP = {
    "Employed": "Wage-Employed",
    "Self-employed": "Self-Employed",
}

_CIVIL_MAP = {
    "Separated": "Separated/Divorced/Annulled",
}

# Old classification options → closest V2021 match
_CLASSIFICATION_MAP = {
    "Persons with Disabilities (PWDs)": None,  # Section 5 in V2021 (TESDA-only)
    "Displaced Worker (Local)": "Displaced Workers",
    "OFW": "Returning/Repatriated Overseas Filipino Workers (OFW)",
    "OFW Dependent": "Overseas Filipino Workers (OFW) Dependent",
    "OFW Repatriate": "Returning/Repatriated Overseas Filipino Workers (OFW)",
    "Victims/Survivors of Human Trafficking": None,  # Not in V2021
    "Rebel Returnees": "Rebel Returnees/Decommissioned Combatants",
    "Solo Parent": None,  # Not in V2021
}


def _normalize(data: dict) -> dict:
    """Normalize old-format field values to V2021 equivalents for PDF overlay."""
    d = dict(data)

    # Educational attainment
    educ = d.get("educationalAttainment", "")
    if educ in _EDUC_MAP:
        d["educationalAttainment"] = _EDUC_MAP[educ]

    # Employment status
    emp = d.get("employmentStatus", "")
    if emp in _EMPLOYMENT_MAP:
        d["employmentStatus"] = _EMPLOYMENT_MAP[emp]

    # Civil status
    civil = d.get("civilStatus", "")
    if civil in _CIVIL_MAP:
        d["civilStatus"] = _CIVIL_MAP[civil]

    # Classifications
    old_cls = d.get("learnerClassification", []) or []
    if old_cls:
        new_cls = []
        for item in old_cls:
            if item in _CLASSIFICATION_MAP:
                mapped = _CLASSIFICATION_MAP[item]
                if mapped and mapped not in new_cls:
                    new_cls.append(mapped)
            else:
                if item not in new_cls:
                    new_cls.append(item)
        d["learnerClassification"] = new_cls

    # Privacy consent backward compat
    if not d.get("privacyConsent") and d.get("certificationAgreed"):
        d["privacyConsent"] = "Agree"

    return d


# ── Drawing helpers ──────────────────────────────────────────────────
# V2021 template uses direct PDF coordinates (origin bottom-left, Y up).
# Page 1: 592 x 837,  Page 2: 593 x 839

def _make_helpers(c_obj):
    """Return txt, txtc, chk, chk_match helper functions bound to a canvas."""

    def txt(x, y, value, size=FONT_SIZE, font=FONT):
        if not value:
            return
        c_obj.setFont(font, size)
        c_obj.drawString(x, y, str(value))

    def txtc(x, y, value, size=FONT_SIZE, font=FONT):
        if not value:
            return
        c_obj.setFont(font, size)
        c_obj.drawCentredString(x, y, str(value))

    def chk(x, y, checked):
        if not checked:
            return
        px, py = x, y
        c_obj.saveState()
        c_obj.setLineWidth(1.5)
        c_obj.line(px + 2, py + 4, px + 5, py + 1)
        c_obj.line(px + 5, py + 1, px + 10, py + 9)
        c_obj.restoreState()

    def chk_match(x, y, value, option):
        if isinstance(value, list):
            chk(x, y, option in value)
        else:
            chk(x, y, value == option)

    return txt, txtc, chk, chk_match


def build_tesda_pdf(data: dict) -> io.BytesIO:
    """Overlay applicant data onto the official TESDA V2021 form template PDF."""

    data = _normalize(data)
    template = PdfReader(str(TEMPLATE_PATH))
    writer = PdfWriter()

    # ── PAGE 1 ─────────────────────────────────────────────────────────
    page1 = template.pages[0]
    W1 = float(page1.mediabox.width)   # 592
    H1 = float(page1.mediabox.height)  # 837

    buf1 = io.BytesIO()
    c = canvas.Canvas(buf1, pagesize=(W1, H1))
    txt, txtc, chk, chk_match = _make_helpers(c)

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 2 — MANPOWER PROFILE
    # ═══════════════════════════════════════════════════════════════════
    # Column centers:  Col1(Last+Ext)≈230  Col2(First)≈380  Col3(Middle)≈520

    # 2.1 Name — centered in boxes (y ≈ 565)
    last = _v(data, "lastName")
    ext = _v(data, "extensionName")
    name_combined = f"{last} {ext}".strip() if ext else last
    txtc(210, 565, name_combined)
    txtc(385, 565, _v(data, "firstName"))
    txtc(520, 565, _v(data, "middleName"))

    # 2.2 Address — Row 1: Street, Barangay, District (y ≈ 515)
    txtc(210, 515, _v(data, "street"))
    txtc(385, 515, _v(data, "barangay"))
    txtc(520, 515, _v(data, "district"))

    # Address — Row 2: City/Municipality, Province, Region (y ≈ 475)
    txtc(210, 475, _v(data, "city"))
    txtc(385, 475, _v(data, "province"))
    txtc(520, 475, _short_region(_v(data, "region")))

    # Email/Facebook, Contact No, Nationality (y ≈ 445)
    email = _v(data, "email")
    fb = _v(data, "facebookAccount")
    email_fb = f"{email} / {fb}" if fb else email
    txtc(210, 445, email_fb, size=SMALL_SIZE)
    txtc(385, 445, _v(data, "contactNo"))
    txtc(520, 445, _v(data, "nationality"))

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 3 — PERSONAL INFORMATION
    # ═══════════════════════════════════════════════════════════════════
    sex = _v(data, "sex")
    civil = _v(data, "civilStatus")
    employment = _v(data, "employmentStatus")
    emp_type = _v(data, "employmentType")

    # 3.1 Sex (checkboxes at x≈33)
    chk_match(33, 366, sex, "Male")
    chk_match(33, 355, sex, "Female")

    # 3.2 Civil Status (checkboxes at x≈126)
    chk_match(126, 366, civil, "Single")
    chk_match(126, 355, civil, "Married")
    chk_match(126, 343, civil, "Separated/Divorced/Annulled")
    chk_match(126, 331, civil, "Widow/er")
    chk_match(126, 320, civil, "Common Law/Live-in")

    # 3.3 Employment Status (checkboxes at x≈265)
    chk_match(265, 356, employment, "Wage-Employed")
    chk_match(265, 344, employment, "Underemployed")
    chk_match(265, 309, employment, "Self-Employed")
    chk_match(265, 298, employment, "Unemployed")

    # Employment Type — only if Wage-Employed or Underemployed (x≈405 left col, x≈480 right col)
    chk_match(393, 356, emp_type, "None")
    chk_match(393, 344, emp_type, "Casual")
    chk_match(393, 332, emp_type, "Probationary")
    chk_match(393, 320, emp_type, "Contractual")
    chk_match(464, 356, emp_type, "Regular")
    chk_match(464, 344, emp_type, "Job Order")
    chk_match(464, 332, emp_type, "Permanent")
    chk_match(464, 320, emp_type, "Temporary")

    # 3.4 Birthdate (y ≈ 280)
    txtc(160, 275, _v(data, "birthMonth"))
    txtc(290, 275, _v(data, "birthDay"))
    txtc(410, 275, _v(data, "birthYear"))
    txtc(520, 275, _v(data, "age"))

    # 3.5 Birthplace (y ≈ 240)
    txtc(195, 235, _v(data, "birthplaceCity"))
    txtc(380, 235, _v(data, "birthplaceProvince"))
    txtc(520, 235 , _short_region(_v(data, "birthplaceRegion")))

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 3.6 — EDUCATIONAL ATTAINMENT
    # ═══════════════════════════════════════════════════════════════════
    educ = _v(data, "educationalAttainment")


    educ_positions = [
        # Column 1
        (26, 183, "No Grade Completed"),
        (26, 163, "Elementary Undergraduate"),
        (26, 148, "Elementary Graduate"),
        (26, 129, "High School Undergraduate"),
        (26, 109, "High School Graduate"),
        # Column 2
        (175, 183, "Junior High (K-12)"),
        (175, 163, "Senior High (K-12)"),
        (175, 148, "Post-Secondary Non-Tertiary/Technical Vocational Course Undergraduate"),
        (175, 129, "Post-Secondary Non-Tertiary/Technical Vocational Course Graduate"),
        # Column 3
        (394, 183, "College Undergraduate"),
        (394, 163, "College Graduate"),
        (394, 148, "Masteral"),
        (394, 129, "Doctorate"),
    ]

    for ex, ey, opt in educ_positions:
        chk_match(ex, ey, educ, opt)

    c.save()
    buf1.seek(0)

    # Merge overlay onto template page 1
    overlay1 = PdfReader(buf1)
    page1.merge_page(overlay1.pages[0])
    writer.add_page(page1)

    # ── PAGE 2 ─────────────────────────────────────────────────────────
    if len(template.pages) > 1:
        page2 = template.pages[1]
        W2 = float(page2.mediabox.width)   # 593
        H2 = float(page2.mediabox.height)  # 839

        buf2 = io.BytesIO()
        c2 = canvas.Canvas(buf2, pagesize=(W2, H2))
        txt2, txtc2, chk2, chk_match2 = _make_helpers(c2)

        # ═══════════════════════════════════════════════════════════════
        # SECTION 4 — LEARNER CLASSIFICATION
        # ═══════════════════════════════════════════════════════════════
        classifications = data.get("learnerClassification", []) or []

        # 3 columns × 8 rows; Col1 x≈47, Col2 x≈225, Col3 x≈415
        # Row spacing ≈ 22 pts, first row y≈757
        cls_positions = [
            # Row 1 (y ≈ 757)
            (25, 755, "4Ps Beneficiary"),
            (202, 755, "Agrarian Reform Beneficiary"),
            (388, 755, "Balik Probinsya"),
            # Row 2 (y ≈ 735)
            (25, 735, "Displaced Workers"),
            (202, 740, "Drug Dependents Surrenderees/Surrenderers"),
            (388, 740, "Family Members of AFP and PNP Killed-in-Action"),
            # Row 3 (y ≈ 713)
            (25, 717, "Family Members of AFP and PNP Wounded-in-Action"),
            (202, 713, "Farmers and Fishermen"),
            (388, 713, "Indigenous People & Cultural Communities"),
            # Row 4 (y ≈ 695)
            (25, 695, "Industry Workers"),
            (202, 696, "Inmates and Detainees"),
            (388, 696, "MILF Beneficiary"),
            # Row 5 (y ≈ 675)
            (25, 678, "Out-of-School-Youth"),
            (202, 682, "Overseas Filipino Workers (OFW) Dependent"),
            (388, 678, "RCEF-RESP"),
            # Row 6 (y ≈ 655)
            (25, 660, "Rebel Returnees/Decommissioned Combatants"),
            (202, 660, "Returning/Repatriated Overseas Filipino Workers (OFW)"),
            (388, 656, "Student"),
            # Row 7 (y ≈ 637)
            (25, 638, "TESDA Alumni"),
            (202, 638, "TVET Trainers"),
            (388, 638, "Uniformed Personnel"),
            # Row 8 (y ≈ 619)
            (25, 619, "Victim of Natural Disasters and Calamities"),
            (202, 619, "Wounded-in-Action AFP & PNP Personnel"),
            (388, 623, "Others"),
        ]

        for cx, cy, opt in cls_positions:
            chk2(cx, cy, opt in classifications)

        # Others specify text
        other_text = _v(data, "classificationOther")
        if other_text and "Others" in classifications:
            txt2(470, 622, other_text, size=SMALL_SIZE)

        # ═══════════════════════════════════════════════════════════════
        # SECTION 7 — COURSE / QUALIFICATION (y ≈ 490)
        # ═══════════════════════════════════════════════════════════════
        txt2(60, 475, _v(data, "course"))

        # ═══════════════════════════════════════════════════════════════
        # SECTION 8 — PRIVACY CONSENT (y ≈ 355)
        # ═══════════════════════════════════════════════════════════════
        consent = _v(data, "privacyConsent")
        # Backward compat: old apps have certificationAgreed
        if not consent and data.get("certificationAgreed"):
            consent = "Agree"
        chk_match2(197, 351, consent, "Agree")
        chk_match2(318, 351, consent, "Disagree")

        c2.save()
        buf2.seek(0)

        overlay2 = PdfReader(buf2)
        page2.merge_page(overlay2.pages[0])
        writer.add_page(page2)

    # Write final PDF
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output


# ── Endpoint ──────────────────────────────────────────────────────────

@router.get("/enrollments/{enrollment_id}/pdf")
async def export_enrollment_pdf(enrollment_id: str, _admin: dict = Depends(verify_jwt)):
    """Generate and return a TESDA MIS 03-01 PDF for an enrollment."""
    try:
        collection = "pending_enrollment_application"
        doc_ref = db.collection(collection).document(enrollment_id).get()

        if not doc_ref.exists:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        data = doc_ref.to_dict()
        # Always compute age from birthdate fields
        data["age"] = _compute_age(data)
        pdf_buf = build_tesda_pdf(data)

        first_name = data.get("firstName", "")
        last_name = data.get("lastName", "")
        filename = f"Tesda Registration {first_name} {last_name}.pdf"

        return StreamingResponse(
            pdf_buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate PDF")
        raise HTTPException(status_code=500, detail=str(e))
