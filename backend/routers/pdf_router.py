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

# Path to the blank TESDA MIS 03-01 form template
TEMPLATE_PATH = Path(__file__).parent.parent / "tesda_files" / "REGISTRATION FORM TESDA.pdf"

FONT = "Helvetica-Bold"
FONT_SIZE = 9
SMALL_SIZE = 8

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

# ── Coordinate System ──────────────────────────────────────────────────
# The template PDF uses transform: 0.75 0 0 -0.75 0 792 cm
# This means: top-left origin, Y increases downward, 0.75x scale.
# Virtual canvas = 816 x 1056 (scaled down to 612 x 792 PDF points).
# Conversion: pdf_x = vx * 0.75,  pdf_y = 792 - vy * 0.75
SCALE = 0.75
PAGE_H = 792.0


def _v(data: dict, key: str, default: str = "") -> str:
    val = data.get(key, default)
    return str(val) if val else default


def _short_region(value: str) -> str:
    """Extract short region name, e.g. 'Region IX (Zamboanga Peninsula)' → 'Region IX'."""
    if "(" in value:
        return value.split("(")[0].strip()
    return value


def build_tesda_pdf(data: dict) -> io.BytesIO:
    """Overlay applicant data onto the official TESDA form template PDF."""

    template = PdfReader(str(TEMPLATE_PATH))
    writer = PdfWriter()

    # ── Page 1 ────────────────────────────────────────────────────────
    page1 = template.pages[0]
    W = float(page1.mediabox.width)
    H = float(page1.mediabox.height)

    buf1 = io.BytesIO()
    c = canvas.Canvas(buf1, pagesize=(W, H))

    # ── Helpers (virtual coords → PDF coords) ──

    def txt(vx, vy, value, size=FONT_SIZE, font=FONT):
        """Draw text at virtual coordinates (template space: top-left, Y-down)."""
        if not value:
            return
        c.setFont(font, size)
        c.drawString(vx * SCALE, PAGE_H - vy * SCALE, str(value))

    def txtc(vx, vy, value, size=FONT_SIZE, font=FONT):
        """Draw centered text at virtual coordinates."""
        if not value:
            return
        c.setFont(font, size)
        c.drawCentredString(vx * SCALE, PAGE_H - vy * SCALE, str(value))

    def chk(vx, vy, checked):
        """Draw a checkmark at virtual coordinates."""
        if not checked:
            return
        px = vx * SCALE
        py = PAGE_H - vy * SCALE
        c.saveState()
        c.setLineWidth(1.5)
        c.line(px + 2, py + 4, px + 5, py + 1)
        c.line(px + 5, py + 1, px + 10, py + 9)
        c.restoreState()

    def chk_match(vx, vy, value, option):
        if isinstance(value, list):
            chk(vx, vy, option in value)
        else:
            chk(vx, vy, value == option)

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 2 — MANPOWER PROFILE
    # ═══════════════════════════════════════════════════════════════════
    # Sub-label positions extracted from template (virtual coords):
    #   "Last Name" vx=297, vy=355 | "First Name" vx=501, vy=355
    #   "Number, Street" vy=399 | "City/Municipality" vy=439
    #   "Email Address" vy=477

    # 2.1 Name — centered in name boxes
    txtc(300, 340, _v(data, "lastName"))
    txtc(510, 340, _v(data, "firstName"))
    txtc(690, 340, _v(data, "middleName"))

    # 2.2 Address — Row 1: Street, Barangay, District (centered)
    txtc(300, 382, _v(data, "street"))
    txtc(510, 382, _v(data, "barangay"))
    txtc(690, 382, _v(data, "district"))

    # Address — Row 2: City/Municipality, Province, Region (centered)
    txtc(300, 422, _v(data, "city"))
    txtc(510, 422, _v(data, "province"))
    txtc(690, 422, _short_region(_v(data, "region")))

    # Email, Contact No, Nationality (centered)
    txtc(300, 460, _v(data, "email"), size=SMALL_SIZE)
    txtc(510, 460, _v(data, "contactNo"))
    txtc(690, 460, _v(data, "nationality"))

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 3 — PERSONAL INFORMATION
    # ═══════════════════════════════════════════════════════════════════
    # Extracted checkbox label positions:
    #   "Male" vx=116, vy=554 | "Female" vy=568
    #   "Single" vx=296, vy=554 | "Married" vy=568 | "Widow/er" vy=581
    #   "Employed" vx=483, vy=554

    sex = _v(data, "sex")
    civil = _v(data, "civilStatus")
    employment = _v(data, "employmentStatus")

    # 3.1 Sex — checkbox ~20 units left of label text
    chk_match(90, 552, sex, "Male") # 90, 552 is good
    chk_match(90, 566, sex, "Female") # 90, 566 is good

    # 3.2 Civil Status
    chk_match(270, 552, civil, "Single") #270, 552 is good
    chk_match(270, 566, civil, "Married") #270, 566 is good
    chk_match(270, 580, civil, "Widow/er") #270, 580 is good
    chk_match(270, 594, civil, "Separated") #270, 594 is good

    # 3.3 Employment Status
    chk_match(458, 552, employment, "Employed") #458, 552 is good
    chk_match(458, 566, employment, "Unemployed") #458, 566 is good
    chk_match(458, 580, employment, "Self-employed") #458, 580 is good

    # 3.4 Birthdate — inside the birth date boxes
    txtc(240, 645, _v(data, "birthMonth"))
    txtc(385, 645, _v(data, "birthDay"))
    txtc(550, 645, _v(data, "birthYear"))
    txtc(690, 645, _v(data, "age"))

    # 3.4 Birthplace — inside the birthplace boxes
    txtc(280, 720, _v(data, "birthplaceCity"))
    txtc(500, 720, _v(data, "birthplaceProvince"))
    txtc(680, 720, _short_region(_v(data, "birthplaceRegion")))

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 3.5 — EDUCATIONAL ATTAINMENT
    # ═══════════════════════════════════════════════════════════════════
    # Extracted positions: vy range 778-814, two rows of 4 options

    educ = _v(data, "educationalAttainment")

    educ_positions = [
        # Row 1 — vy ≈ 788 (columns aligned with Row 2)
        (67, 776, "No Grade Completed / Pre-School (Nursery/Kinder/Prep)"), #67, 776 is good
        (232, 782, "Elementary Level"), #232, 782 is good
        (429, 782, "Elementary Graduate"), #429, 782 is good
        (598, 782, "High School Level"), #598, 782 is good
        # Row 2 — vy ≈ 812
        (67, 812, "High School Graduate"),
        (232, 812, "Post-Secondary Level/Graduate"),
        (429, 812, "College Level"), #429, 812 is good
        (598, 812, "College Graduate or Higher"), #598, 812 is good
    ]

    for ex, ey, opt in educ_positions:
        chk_match(ex, ey, educ, opt)

    # ═══════════════════════════════════════════════════════════════════
    # SECTION 4 — LEARNER CLASSIFICATION
    # ═══════════════════════════════════════════════════════════════════
    # Extracted: "Persons w/ Disabilities" (114, 880), "Solo Parent" (554, 892)
    #            "OFW" (115, 939)

    classifications = data.get("learnerClassification", []) or []

    cls_positions = [
        # Row 1 — vy ≈ 882
        (90, 878, "Persons with Disabilities (PWDs)"), #90, 878 is good
        (267, 890, "OFW Repatriate"), #267, 890 is good
        (530, 890, "Solo Parent"),
        # Row 2 — vy ≈ 905
        (90, 914, "Displaced Worker (Local)"), #90, 914 is good
        (267, 914, "Victims/Survivors of Human Trafficking"), #267, 914 is good
        (530, 914, "Others"),
        # Row 3 — vy ≈ 928
        (90, 938, "OFW"), #90 , 938 is good
        (267, 938, "Indigenous People & Cultural Communities"), #267, 938 is good
        # Row 4 — vy ≈ 951
        (90, 960, "OFW Dependent"), #90, 960 is good
        (267, 960, "Rebel Returnees"), #267, 960 is good
    ]

    for cx, cy, opt in cls_positions:
        chk(cx, cy, opt in classifications)

    # Others specify text
    other_text = _v(data, "classificationOther")
    if other_text and "Others" in classifications:
        txtc(540, 938, other_text, size=SMALL_SIZE)

    c.save()
    buf1.seek(0)

    # Merge overlay onto template page 1
    overlay1 = PdfReader(buf1)
    page1.merge_page(overlay1.pages[0])
    writer.add_page(page1)

    # ── Page 2 ────────────────────────────────────────────────────────
    # Same coordinate transform as page 1

    if len(template.pages) > 1:
        page2 = template.pages[1]
        W2 = float(page2.mediabox.width)
        H2 = float(page2.mediabox.height)

        buf2 = io.BytesIO()
        c2 = canvas.Canvas(buf2, pagesize=(W2, H2))

        def txt2(vx, vy, value, size=FONT_SIZE, font=FONT):
            if not value:
                return
            c2.setFont(font, size)
            c2.drawString(vx * SCALE, PAGE_H - vy * SCALE, str(value))

        def chk2(vx, vy, checked):
            if not checked:
                return
            px = vx * SCALE
            py = PAGE_H - vy * SCALE
            c2.saveState()
            c2.setLineWidth(1.5)
            c2.line(px + 2, py + 4, px + 5, py + 1)
            c2.line(px + 5, py + 1, px + 10, py + 9)
            c2.restoreState()

        # Section 5 — NCAE/YP4SC
        # Extracted: "Yes" at (347, 89), question header at (70, 89)
        ncae_taken = data.get("ncaeTaken", False)
        chk2(318, 89, ncae_taken)
        chk2(555, 89, not ncae_taken)
        txt2(170, 112, _v(data, "ncaeWhere"))
        txt2(170, 130, _v(data, "ncaeWhen"))

        # Section 6 — Course/Qualification
        txt2(300, 160, _v(data, "course"))

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
