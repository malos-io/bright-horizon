"""
TESDA NTTC Registry + TVI Scraper -> Firestore
Scrapes trainers and TVIs from tesda.gov.ph, filtered for Region IX,
and syncs results to Firestore with upsert (merge).

Usage:
  - As Cloud Run Job: runs automatically via Cloud Scheduler or admin trigger
  - Locally: python scrape_tesda_nttc.py
"""

import re
import time

import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import firestore

# Initialize Firebase (uses default credentials on Cloud Run)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

INSTRUCTORS_COLLECTION = "tesda_instructors"
TVIS_COLLECTION = "tesda_tvis"
SYNC_META_COLLECTION = "tesda_sync_metadata"

BASE_URL = "https://www.tesda.gov.ph/NTTC/Result"
TVI_URL = "https://www.tesda.gov.ph/Tvi/Result"
DETAIL_URL = "https://www.tesda.gov.ph/NTTC/Details"

QUALIFICATIONS = [
    "EVENTS MANAGEMENT SERVICES NC III",
    "BOOKKEEPING NC III",
    "HOUSEKEEPING NC III",
    "HILOT (WELLNESS MASSAGE) NC II",
]


def scrape_nttc_page(session, page_num, qual_filter):
    """Scrape one page of NTTC results."""
    params = {"page": page_num, "qualFilter": qual_filter}
    try:
        r = session.get(BASE_URL, params=params, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"  Error fetching NTTC page {page_num}: {e}")
        return [], 0

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        return [], 0

    rows = table.find_all("tr")[1:]
    results = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 4:
            name = cells[0].get_text(strip=True)
            cert_num = cells[1].get_text(strip=True)
            qual = cells[2].get_text(strip=True)
            detail_link = cells[3].find("a")
            detail_id = ""
            if detail_link:
                href = detail_link.get("href", "")
                match = re.search(r"/Details/(\d+)", href)
                if match:
                    detail_id = match.group(1)
            results.append(
                {
                    "name": name,
                    "cert_num": cert_num,
                    "qualification": qual,
                    "detail_id": detail_id,
                }
            )

    total_pages = 0
    for link in soup.find_all("a", href=True):
        match = re.search(r"page=(\d+)", link.get("href", ""))
        if match:
            total_pages = max(total_pages, int(match.group(1)))

    return results, total_pages


def scrape_nttc_detail(session, detail_id):
    """Scrape a trainer's NTTC detail page for region and certificate info."""
    try:
        r = session.get(f"{DETAIL_URL}/{detail_id}", timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"      Error fetching detail {detail_id}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    info = {}
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).rstrip(":")
            value = cells[1].get_text(strip=True)
            info[label] = value

    return {
        "region": info.get("Region", ""),
        "nc_cert": info.get("NC Certificate", ""),
        "valid_until_nc": info.get("Valid Until (NC)", ""),
        "nttc_cert": info.get("NTTC Certificate", ""),
        "valid_until_nttc": info.get("Valid Until (NTTC)", ""),
    }


REGION_IX_ADDRESS_MARKERS = [
    "zamboanga del norte",
    "zamboanga del sur",
    "zamboanga sibugay",
    "zamboanga city",
    "dipolog city",
    "dipolog",
    "dapitan city",
    "dapitan",
    "pagadian city",
    "pagadian",
    "isabela city",
    "ipil",
]


def is_region_ix_address(address):
    """Check if a TVI address belongs to Region IX by inspecting last 1-2 parts."""
    if not address:
        return False
    parts = [p.strip().lower() for p in address.split(",")]
    # Check last 2 parts (e.g. "Dipolog City, Zamboanga del Norte")
    tail = parts[-2:] if len(parts) >= 2 else parts[-1:]
    for part in tail:
        for marker in REGION_IX_ADDRESS_MARKERS:
            if marker in part:
                return True
    return False


def scrape_tvi_page_v2(session, page_num, qual_filter, loc_filter="zamboanga"):
    """Scrape TVI page using DOM structure."""
    params = {
        "page": page_num,
        "SearchCourse": qual_filter,
        "SearchLoc": loc_filter,
        "SearchIns": "",
    }
    try:
        r = session.get(TVI_URL, params=params, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"  Error fetching TVI page {page_num} ({loc_filter}): {e}")
        return [], 0

    soup = BeautifulSoup(r.text, "html.parser")
    entries = []

    for desc_div in soup.find_all("div", class_="directory-description"):
        h4 = desc_div.find("h4")
        school = h4.get_text(strip=True) if h4 else ""

        course_span = desc_div.find("span")
        course = course_span.get_text(strip=True) if course_span else ""

        trainer = ""
        trainer_span = desc_div.find(
            "span", string=re.compile(r"Trainer", re.IGNORECASE)
        )
        if trainer_span and trainer_span.next_sibling:
            trainer = trainer_span.next_sibling.strip().lstrip(":").strip()

        address = ""
        phone = ""
        info_div = desc_div.find_next_sibling("div", class_="directory-info")
        if not info_div:
            parent = desc_div.parent
            if parent:
                info_div = parent.find("div", class_="directory-info")
        if info_div:
            for p in info_div.find_all("p"):
                icon = p.find("span", class_=re.compile(r"fa-"))
                icon_class = " ".join(icon.get("class", [])) if icon else ""
                text = p.get_text(strip=True)
                if "fa-map-marker" in icon_class:
                    address = text
                elif "fa-phone" in icon_class:
                    phone = text

        entries.append(
            {
                "school": school,
                "course": course or qual_filter,
                "trainer": trainer,
                "address": address,
                "phone": phone,
                "source_page": f"TVI p{page_num} ({loc_filter})",
            }
        )

    total_pages = 0
    for link in soup.find_all("a", href=True):
        match = re.search(r"page=(\d+)", link.get("href", ""))
        if match:
            total_pages = max(total_pages, int(match.group(1)))

    return entries, total_pages


def scrape_qualification(session, qual_filter, loc_filters):
    """Scrape NTTC and TVI data for a single qualification."""
    # --- NTTC Registry ---
    all_trainers = []
    print(f"\n  [NTTC] Scraping: {qual_filter}")

    results, total_pages = scrape_nttc_page(session, 1, qual_filter)
    all_trainers.extend(results)
    print(f"    Page 1/{total_pages}: {len(results)} trainers")

    for page in range(2, total_pages + 1):
        results, _ = scrape_nttc_page(session, page, qual_filter)
        all_trainers.extend(results)
        print(
            f"    Page {page}/{total_pages}: {len(results)} trainers (total: {len(all_trainers)})"
        )
        time.sleep(0.5)

    print(f"    NTTC Total: {len(all_trainers)}")

    # Check every trainer's detail page to find Region IX
    print(f"    Checking {len(all_trainers)} trainers via detail pages...")
    region_ix_trainers = []
    for idx, t in enumerate(all_trainers, 1):
        if not t["detail_id"]:
            continue
        detail = scrape_nttc_detail(session, t["detail_id"])
        if detail:
            t.update(detail)
            if detail["region"] == "IX":
                region_ix_trainers.append(t)
        if idx % 100 == 0:
            print(
                f"      Checked {idx}/{len(all_trainers)} — Region IX so far: {len(region_ix_trainers)}"
            )
        time.sleep(0.3)

    print(f"    Confirmed Region IX: {len(region_ix_trainers)} trainers")

    # --- TVI Registry ---
    tvi_entries = []
    print(f"\n  [TVI] Scraping institutions for: {qual_filter}")

    for loc in loc_filters:
        print(f"    Location filter: '{loc}'")
        results, total_pages = scrape_tvi_page_v2(session, 1, qual_filter, loc)
        tvi_entries.extend(results)
        if results:
            print(f"      Page 1/{total_pages}: {len(results)} entries")

        for page in range(2, total_pages + 1):
            results, _ = scrape_tvi_page_v2(session, page, qual_filter, loc)
            if results:
                tvi_entries.extend(results)
                print(f"      Page {page}/{total_pages}: {len(results)} entries")
            time.sleep(0.5)

    # Deduplicate TVI entries by school+trainer
    seen = set()
    unique_tvi = []
    for entry in tvi_entries:
        key = (entry["school"], entry["trainer"], entry.get("source_page", ""))
        if key not in seen:
            seen.add(key)
            unique_tvi.append(entry)

    print(f"    TVI Total (deduplicated): {len(unique_tvi)} entries")

    # Verify Region IX by checking address (last 1-2 comma parts)
    verified_tvi = []
    skipped = []
    for entry in unique_tvi:
        if is_region_ix_address(entry["address"]):
            verified_tvi.append(entry)
        else:
            skipped.append(entry)
    if skipped:
        print(f"    Skipped {len(skipped)} non-Region IX TVIs:")
        for s in skipped:
            print(f"      - {s['school']} | {s['address']}")

    print(f"    TVI Verified Region IX: {len(verified_tvi)} entries")

    return region_ix_trainers, verified_tvi


def slugify(text):
    """Create a Firestore-safe document ID from text."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:128]


def sync_to_firestore(qual_data):
    """Sync scraped data to Firestore with upsert (merge)."""
    print("\n" + "=" * 60)
    print("Syncing to Firestore")
    print("=" * 60)

    # Combine all qualifications
    all_instructors = []
    all_tvi = []
    for data in qual_data.values():
        all_instructors.extend(data["region_ix"])
        all_tvi.extend(data["tvi"])

    now = firestore.SERVER_TIMESTAMP

    # Step 1: Mark all existing docs as inactive
    print("\nMarking existing instructors as inactive...")
    for doc in db.collection(INSTRUCTORS_COLLECTION).stream():
        doc.reference.update({"active": False})

    print("Marking existing TVIs as inactive...")
    for doc in db.collection(TVIS_COLLECTION).stream():
        doc.reference.update({"active": False})

    # Step 2: Upsert instructors (doc ID = detail_id)
    print(f"\nUpserting {len(all_instructors)} instructors...")
    for t in all_instructors:
        doc_id = t.get("detail_id", "")
        if not doc_id:
            continue

        db.collection(INSTRUCTORS_COLLECTION).document(doc_id).set(
            {
                "name": t["name"],
                "course": t["qualification"],
                "region": t.get("region", "IX"),
                "cert_num": t.get("cert_num", ""),
                "nc_cert": t.get("nc_cert", ""),
                "valid_until_nc": t.get("valid_until_nc", ""),
                "nttc_cert": t.get("nttc_cert", ""),
                "valid_until_nttc": t.get("valid_until_nttc", ""),
                "detail_link": f"https://www.tesda.gov.ph/NTTC/Details/{doc_id}",
                "active": True,
                "last_synced": now,
            },
            merge=True,
        )

    # Step 3: Aggregate TVIs by school+course, then upsert
    tvi_map = {}
    for t in all_tvi:
        key = slugify(f"{t['school']}_{t['course']}")
        if not key:
            continue
        if key not in tvi_map:
            tvi_map[key] = {
                "school": t["school"],
                "course": t["course"],
                "trainers": [],
                "address": t["address"],
                "phone": t["phone"],
            }
        if t["trainer"] and t["trainer"] not in tvi_map[key]["trainers"]:
            tvi_map[key]["trainers"].append(t["trainer"])
        if t["address"] and not tvi_map[key]["address"]:
            tvi_map[key]["address"] = t["address"]
        if t["phone"] and not tvi_map[key]["phone"]:
            tvi_map[key]["phone"] = t["phone"]

    print(f"Upserting {len(tvi_map)} TVI entries...")
    for doc_id, data in tvi_map.items():
        db.collection(TVIS_COLLECTION).document(doc_id).set(
            {
                "school": data["school"],
                "course": data["course"],
                "trainers": data["trainers"],
                "address": data["address"],
                "phone": data["phone"],
                "active": True,
                "last_synced": now,
            },
            merge=True,
        )

    # Step 4: Update sync metadata
    db.collection(SYNC_META_COLLECTION).document("latest").set(
        {
            "synced_at": now,
            "instructor_count": len(all_instructors),
            "tvi_count": len(tvi_map),
            "qualifications": list(qual_data.keys()),
        }
    )

    print(f"\nSync complete!")
    print(f"  Instructors: {len(all_instructors)}")
    print(f"  TVIs: {len(tvi_map)}")


def main():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )

    # All Region IX cities and municipalities
    loc_filters = [
        # Cities
        "zamboanga", "dipolog", "dapitan", "pagadian", "isabela city",
        # Zamboanga del Norte municipalities
        "baliguian", "godod", "gutalac", "jose dalman", "kalawit",
        "katipunan", "la libertad", "labason", "leon b. postigo", "liloy",
        "manukan", "mutia", "pinan", "polanco", "roxas",
        "rizal", "salug", "sergio osmena", "siayan", "sibuco",
        "sibutad", "sindangan", "siocon", "sirawai", "tampilisan",
        # Zamboanga del Sur municipalities
        "aurora", "bayog", "dimataling", "dinas", "dumalinao",
        "dumingag", "guipos", "josefina", "kumalarang", "labangan",
        "lakewood", "lapuyan", "mahayag", "margosatubig", "midsalip",
        "molave", "pitogo", "ramon magsaysay", "san miguel", "san pablo",
        "sominot", "tabina", "tambulig", "tigbao", "tukuran", "sagun",
        # Zamboanga Sibugay municipalities
        "alicia", "buug", "diplahan", "imelda", "ipil",
        "kabasalan", "mabuhay", "malangas", "naga", "olutanga",
        "payao", "roseller lim", "siay", "talusan", "titay", "tungawan",
    ]

    # Scrape each qualification
    qual_data = {}
    for qual in QUALIFICATIONS:
        print("=" * 60)
        print(f"Scraping: {qual}")
        print("=" * 60)
        region_ix, tvi = scrape_qualification(session, qual, loc_filters)
        qual_data[qual] = {
            "region_ix": region_ix,
            "tvi": tvi,
        }

    # Sync to Firestore
    sync_to_firestore(qual_data)


if __name__ == "__main__":
    main()
