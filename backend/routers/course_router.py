import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from firebase_admin import firestore
from schemas.course_schema import Course, CourseModule, CourseSchedule, Instructor
from reusable_components.firebase import db
from reusable_components.auth import verify_jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["courses"])

# Instructors
INSTRUCTORS = {
    "default": Instructor(
        name="TBA",
        title="Certified TESDA Trainer",
        bio="Our qualified trainers are certified by TESDA with extensive industry experience.",
        image="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop"
    ),
}

# Courses
COURSES = [
    Course(
        id="1",
        slug="bookkeeping-nc-iii",
        title="Bookkeeping NC III",
        short_description="Develop foundational bookkeeping skills and competencies for recording, posting, and preparing financial reports.",
        description="""This comprehensive Bookkeeping NC III program provides the essential skills and competencies required to perform bookkeeping job roles effectively.

You will learn effective workplace practices and job-related fundamentals including journalizing transactions, posting entries both manually and digitally, preparing trial balances, and creating financial reports.

This TESDA-accredited program prepares you for careers in accounting departments, small businesses, and financial institutions.""",
        image="/images/courses/bookkeeping.png",
        duration_weeks=6,
        total_hours=292,
        price=0,
        discounted_price=None,
        category="Business & Finance",
        level="Beginner",
        certification="TESDA NC III Certified",
        class_size=30,
        start_dates=["TBA"],
        schedule=[
            CourseSchedule(day="Self-paced", time="Online", duration="Flexible"),
        ],
        modules=[
            CourseModule(
                title="Introduction to Bookkeeping",
                description="Essential skills and competencies for bookkeeping roles, effective workplace practices and fundamentals",
                duration_hours=32
            ),
            CourseModule(
                title="Journalizing Transactions",
                description="Logging and recording business transactions in an accounting journal, best practices and procedures",
                duration_hours=58
            ),
            CourseModule(
                title="Posting Transactions",
                description="Posting transactions manually and digitally, foundational knowledge on format and procedures",
                duration_hours=58
            ),
            CourseModule(
                title="Preparing Trial Balance",
                description="Listing accounts, transferring and summarizing trial balances from a ledger, key considerations",
                duration_hours=48
            ),
            CourseModule(
                title="Preparing Financial Reports",
                description="Preparing financial reports manually, guidance on report preparation procedures",
                duration_hours=58
            ),
            CourseModule(
                title="Reviewing Internal Control System",
                description="Reviewing and determining extent of compliance with a firm's internal control manual, effectiveness assessment",
                duration_hours=38
            ),
        ],
        requirements=[
            "At least 18 years old",
            "High school graduate or equivalent",
            "Basic Math/Arithmetic Proficiency",
            "Basic Computer Literacy (MS Excel)",
            "Analytical Skills",
        ],
        what_you_learn=[
            "Recording business transactions in accounting journals",
            "Posting transactions manually and using digital tools",
            "Preparing and summarizing trial balances",
            "Creating financial reports",
            "Understanding internal control systems",
            "Workplace best practices for bookkeepers",
        ],
        career_opportunities=[
            "Bookkeeper",
            "Accounting Clerk",
            "Accounts Payable/Receivable Clerk",
            "Junior Accountant",
            "Financial Record Keeper",
            "Small Business Bookkeeper",
        ],
        instructor=INSTRUCTORS["default"],
        enrolled_count=0,
        rating=0,
        reviews_count=0
    ),
    Course(
        id="2",
        slug="events-management-nc-iii",
        title="Events Management Services NC III",
        short_description="Learn to coordinate events, functions and conferences in venues such as hotels, conference centers, restaurants and resorts.",
        description="""This Events Management Services NC III program trains you to plan and organize events in different venues such as conference centers, hotels, motels, restaurants, clubs, resorts and luxury liners.

You will develop competencies in event planning including developing event proposals, concepts and programs, selecting venues and sites, and providing on-site event management services.

This TESDA-accredited qualification prepares you for careers in the tourism and hospitality sector as an events coordinator or manager.""",
        image="/images/courses/events-management.png",
        duration_weeks=2,
        total_hours=108,
        price=0,
        discounted_price=None,
        category="Tourism & Hospitality",
        level="Intermediate",
        certification="TESDA NC III Certified",
        class_size=25,
        start_dates=["TBA"],
        schedule=[
            CourseSchedule(day="Self-paced", time="Online", duration="Flexible"),
        ],
        modules=[
            CourseModule(
                title="Participate in Workplace Communication",
                description="Develop skills for effective workplace communication in events management settings",
                duration_hours=20
            ),
            CourseModule(
                title="Plan and Develop Event Proposal or Bid",
                description="Learn to plan and develop proposals and bids for staging meetings and events",
                duration_hours=24
            ),
            CourseModule(
                title="Develop Event Concept and Program",
                description="Create comprehensive event concepts and detailed program schedules",
                duration_hours=20
            ),
            CourseModule(
                title="Select Event Venue and Site",
                description="Evaluate and select appropriate venues and sites for different event types",
                duration_hours=16
            ),
            CourseModule(
                title="Provide On-site Event Management",
                description="Manage contractors, coordinate logistics, and oversee event execution",
                duration_hours=20
            ),
            CourseModule(
                title="Update Event Industry Knowledge",
                description="Stay current with event industry trends, protocols, and best practices",
                duration_hours=8
            ),
        ],
        requirements=[
            "At least 18 years old",
            "High school graduate or equivalent",
            "Effective Communication Skills (English/Filipino)",
            "Organizational and Time-Management Skills",
            "Basic Computer Literacy (MS Word/PowerPoint)",
        ],
        what_you_learn=[
            "Planning and developing event proposals and bids",
            "Creating event concepts and detailed programs",
            "Venue selection and site evaluation",
            "On-site event management and coordination",
            "Managing contractors and service providers",
            "Event industry protocols and standards",
        ],
        career_opportunities=[
            "Events Coordinator",
            "Events Manager",
            "Conference Organizer",
            "Wedding Planner",
            "Corporate Events Specialist",
            "Hotel Events Staff",
        ],
        instructor=INSTRUCTORS["default"],
        enrolled_count=0,
        rating=0,
        reviews_count=0
    ),
    Course(
        id="3",
        slug="housekeeping-nc-iii",
        title="Housekeeping NC III",
        short_description="Learn professional housekeeping skills for hotels, resorts, and other hospitality establishments.",
        description="""This comprehensive Housekeeping NC III program prepares you for careers in the hospitality industry with essential housekeeping skills and competencies.

You will learn professional cleaning techniques, room preparation, guest service excellence, and workplace health and safety practices required in hotels, resorts, hospitals, and other establishments.

This TESDA-accredited program equips you with the skills needed to work as a professional housekeeper in various hospitality settings.""",
        image="/images/courses/housekeeping.png",
        duration_weeks=9,
        total_hours=436,
        price=0,
        discounted_price=None,
        category="Tourism & Hospitality",
        level="Beginner",
        certification="TESDA NC III Certified",
        class_size=25,
        start_dates=["TBA"],
        schedule=[
            CourseSchedule(day="Self-paced", time="Online", duration="Flexible"),
        ],
        modules=[
            CourseModule(
                title="Participate in Workplace Communication",
                description="Develop effective communication skills in housekeeping settings",
                duration_hours=60
            ),
            CourseModule(
                title="Work in a Team Environment",
                description="Learn to work effectively with colleagues and supervisors",
                duration_hours=56
            ),
            CourseModule(
                title="Practice Career Professionalism",
                description="Develop professional attitudes and workplace ethics",
                duration_hours=56
            ),
            CourseModule(
                title="Practice Occupational Health and Safety Procedures",
                description="Learn workplace safety protocols and emergency procedures",
                duration_hours=56
            ),
            CourseModule(
                title="Clean and Prepare Rooms for Guests",
                description="Master techniques for cleaning and preparing guest rooms to standards",
                duration_hours=72
            ),
            CourseModule(
                title="Provide Housekeeping Services to Guests",
                description="Learn guest service protocols and responding to guest requests",
                duration_hours=64
            ),
            CourseModule(
                title="Provide Valet/Butler Service",
                description="Develop skills in providing personalized guest services",
                duration_hours=72
            ),
        ],
        requirements=[
            "At least 18 years old",
            "High school graduate or equivalent",
            "Physically fit for housekeeping duties",
            "Good communication skills",
            "Attention to detail",
        ],
        what_you_learn=[
            "Professional room cleaning and preparation techniques",
            "Guest service excellence and etiquette",
            "Workplace health and safety procedures",
            "Linen and laundry management",
            "Valet and butler service skills",
            "Effective workplace communication",
        ],
        career_opportunities=[
            "Room Attendant/Housekeeper",
            "Housekeeping Supervisor",
            "Hotel/Resort Housekeeping Staff",
            "Hospital Housekeeper",
            "Institutional Housekeeper",
            "Private Household Staff",
        ],
        instructor=INSTRUCTORS["default"],
        enrolled_count=0,
        rating=0,
        reviews_count=0,
        is_coming_soon=True
    ),
    Course(
        id="4",
        slug="hilot-wellness-nc-ii",
        title="Hilot (Wellness Massage) NC II",
        short_description="Learn traditional Filipino wellness massage techniques for health, relaxation, and therapeutic purposes.",
        description="""This comprehensive Hilot (Wellness Massage) NC II program trains you in traditional Filipino healing and wellness massage techniques.

You will learn the fundamentals of hilot, traditional massage strokes, body assessment, and therapeutic applications for wellness and health maintenance. This includes both theoretical knowledge and practical skills in traditional Filipino healing arts.

This TESDA-accredited program prepares you for careers in wellness centers, spas, resorts, and health facilities as a certified hilot practitioner.""",
        image="/images/courses/hilot.png",
        duration_weeks=2,
        total_hours=120,
        price=0,
        discounted_price=None,
        category="Health & Wellness",
        level="Beginner",
        certification="TESDA NC II Certified",
        class_size=20,
        start_dates=["TBA"],
        schedule=[
            CourseSchedule(day="Self-paced", time="Online", duration="Flexible"),
        ],
        modules=[
            CourseModule(
                title="Participate in Workplace Communication",
                description="Develop effective communication skills with clients and colleagues",
                duration_hours=16
            ),
            CourseModule(
                title="Work in a Team Environment",
                description="Learn to collaborate effectively in wellness settings",
                duration_hours=12
            ),
            CourseModule(
                title="Practice Career Professionalism",
                description="Develop professional ethics and workplace standards",
                duration_hours=10
            ),
            CourseModule(
                title="Practice Occupational Health and Safety Procedures",
                description="Learn safety protocols and hygiene standards for wellness massage",
                duration_hours=14
            ),
            CourseModule(
                title="Perform Hilot/Wellness Massage",
                description="Master traditional hilot techniques, strokes, and therapeutic applications",
                duration_hours=48
            ),
            CourseModule(
                title="Provide Aftercare Advice",
                description="Learn to provide post-treatment care and wellness recommendations",
                duration_hours=20
            ),
        ],
        requirements=[
            "At least 18 years old",
            "High school graduate or equivalent",
            "Physically fit for manual work",
            "Good communication and interpersonal skills",
            "Interest in traditional Filipino healing arts",
            "No history of infectious diseases",
        ],
        what_you_learn=[
            "Traditional Filipino hilot massage techniques",
            "Body assessment and palpation skills",
            "Therapeutic massage strokes and applications",
            "Client consultation and needs assessment",
            "Health and safety in wellness massage",
            "Aftercare advice and wellness recommendations",
        ],
        career_opportunities=[
            "Hilot Practitioner",
            "Wellness Massage Therapist",
            "Spa Therapist",
            "Resort Wellness Staff",
            "Health Center Massage Therapist",
            "Self-employed Hilot Specialist",
        ],
        instructor=INSTRUCTORS["default"],
        enrolled_count=0,
        rating=0,
        reviews_count=0,
        is_coming_soon=True
    ),
]

# Build a lookup by slug for quick access
_COURSES_BY_SLUG = {c.slug: c for c in COURSES}


# ── Batch-based course overrides (cached) ────────────────────────────

_overrides_cache: dict | None = None
_overrides_cache_ts: float = 0
_OVERRIDES_TTL = 86400  # 24 hours


def _get_course_overrides() -> dict:
    """Read active/enrollment_closed batches as course overrides.

    Results are cached for 10 minutes to avoid hitting Firestore on
    every public page load. Admin batch mutations (create/edit/close)
    call _invalidate_overrides_cache() to force a refresh.
    """
    global _overrides_cache, _overrides_cache_ts

    now = time.monotonic()
    if _overrides_cache is not None and (now - _overrides_cache_ts) < _OVERRIDES_TTL:
        return _overrides_cache

    try:
        collection = "course_batches"
        docs = (
            db.collection(collection)
            .where("status", "in", ["active", "enrollment_closed"])
            .stream()
        )
        result = {}
        for doc in docs:
            data = doc.to_dict()
            slug = data.get("course_slug")
            if not slug:
                continue
            override = {}
            if data.get("start_date"):
                override["start_dates"] = [data["start_date"]]
            if "enrollment_deadline" in data:
                override["enrollment_deadline"] = data["enrollment_deadline"]
            if data.get("instructor"):
                override["instructor"] = data["instructor"]
            result[slug] = override

        _overrides_cache = result
        _overrides_cache_ts = now
        return result
    except Exception as e:
        logger.warning("Failed to fetch course overrides from batches: %s", e)
        return _overrides_cache or {}


def _invalidate_overrides_cache():
    """Force the next _get_course_overrides() call to hit Firestore."""
    global _overrides_cache, _overrides_cache_ts
    _overrides_cache = None
    _overrides_cache_ts = 0


def _apply_overrides(course: Course, overrides: dict) -> Course:
    """Return a new Course with Firestore overrides merged in."""
    override = overrides.get(course.slug)
    if not override:
        return course
    data = course.model_dump()
    if "start_dates" in override:
        data["start_dates"] = override["start_dates"]
    if "enrollment_deadline" in override:
        data["enrollment_deadline"] = override["enrollment_deadline"]
    if "instructor" in override:
        base_instructor = data["instructor"]
        base_instructor.update(override["instructor"])
        data["instructor"] = base_instructor
    return Course(**data)


def _get_active_batch(slug: str):
    """Return the active or enrollment_closed batch doc for a course, or None."""
    collection = "course_batches"
    docs = list(
        db.collection(collection)
        .where("course_slug", "==", slug)
        .where("status", "in", ["active", "enrollment_closed"])
        .limit(1)
        .stream()
    )
    return docs[0] if docs else None


# ── Public endpoints ──────────────────────────────────────────────────


@router.get("/courses", response_model=list[Course])
def get_courses():
    overrides = _get_course_overrides()
    return [_apply_overrides(c, overrides) for c in COURSES]


@router.get("/categories")
def get_categories():
    categories = list(set(course.category for course in COURSES))
    return categories


@router.get("/courses/category/{category}", response_model=list[Course])
def get_courses_by_category(category: str):
    overrides = _get_course_overrides()
    return [_apply_overrides(c, overrides) for c in COURSES if c.category.lower() == category.lower()]


@router.get("/courses/{slug}", response_model=Course)
def get_course(slug: str):
    course = _COURSES_BY_SLUG.get(slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    overrides = _get_course_overrides()
    return _apply_overrides(course, overrides)


# ── Admin: courses summary ────────────────────────────────────────────


@router.get("/courses-summary")
def get_courses_summary(_admin: dict = Depends(verify_jwt)):
    """Get all courses with batch summary stats for the admin courses list."""
    overrides = _get_course_overrides()
    merged_courses = [_apply_overrides(c, overrides) for c in COURSES]

    # Get all batches to compute counts per course
    batch_collection = "course_batches"
    all_batches = list(db.collection(batch_collection).stream())

    # Build per-slug stats from batches
    batch_stats = {}
    for bdoc in all_batches:
        bdata = bdoc.to_dict()
        bslug = bdata.get("course_slug")
        if not bslug:
            continue
        if bslug not in batch_stats:
            batch_stats[bslug] = {"total": 0, "completed": 0, "active_status": None}
        batch_stats[bslug]["total"] += 1
        if bdata.get("status") == "completed":
            batch_stats[bslug]["completed"] += 1
        if bdata.get("status") in ("active", "enrollment_closed"):
            batch_stats[bslug]["active_status"] = bdata["status"]

    # Count completed students per course from enrollments
    enrollment_collection = "pending_enrollment_application"

    results = []
    for course in merged_courses:
        docs = (
            db.collection(enrollment_collection)
            .where("course", "==", course.title)
            .where("status", "==", "completed")
            .stream()
        )
        total_students = sum(1 for _ in docs)

        current_start = course.start_dates[0] if course.start_dates else "TBA"
        stats = batch_stats.get(course.slug, {})

        results.append({
            "slug": course.slug,
            "title": course.title,
            "category": course.category,
            "current_start_date": current_start,
            "batch_count": stats.get("total", 0),
            "total_completed_students": total_students,
            "active_batch_status": stats.get("active_status"),
            "instructor": course.instructor.model_dump(),
            "class_size": course.class_size,
            "duration_weeks": course.duration_weeks,
            "total_hours": course.total_hours,
        })

    return results


# ── Admin: batch lifecycle ────────────────────────────────────────────


@router.post("/courses/{slug}/batches")
def create_batch(slug: str, body: dict = Body(...), admin: dict = Depends(verify_jwt)):
    """Start a new class batch for a course."""
    if slug not in _COURSES_BY_SLUG:
        raise HTTPException(status_code=404, detail="Course not found")

    # Ensure no active batch already exists
    existing = _get_active_batch(slug)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="An active batch already exists for this course. Close it before starting a new one.",
        )

    start_date = body.get("start_date")
    if not start_date:
        raise HTTPException(status_code=400, detail="start_date is required")

    instructor = body.get("instructor", {})
    default_inst = INSTRUCTORS["default"]

    batch_data = {
        "course_slug": slug,
        "status": "active",
        "start_date": start_date,
        "enrollment_deadline": body.get("enrollment_deadline"),
        "instructor": {
            "name": instructor.get("name") or default_inst.name,
            "title": instructor.get("title") or default_inst.title,
            "bio": instructor.get("bio") or default_inst.bio,
            "image": instructor.get("image") or default_inst.image,
        },
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "closed_enrollment_at": None,
        "completed_at": None,
        "created_by": admin.get("sub", "unknown"),
    }

    collection = "course_batches"
    _, doc_ref = db.collection(collection).add(batch_data)

    _invalidate_overrides_cache()
    return {"message": "Batch created", "batch_id": doc_ref.id}


@router.patch("/courses/{slug}/batches/{batch_id}")
def edit_batch(slug: str, batch_id: str, body: dict = Body(...), _admin: dict = Depends(verify_jwt)):
    """Edit an active or enrollment_closed batch."""
    if slug not in _COURSES_BY_SLUG:
        raise HTTPException(status_code=404, detail="Course not found")

    collection = "course_batches"
    doc_ref = db.collection(collection).document(batch_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Batch not found")

    data = doc.to_dict()
    if data.get("course_slug") != slug:
        raise HTTPException(status_code=400, detail="Batch does not belong to this course")
    if data.get("status") not in ("active", "enrollment_closed"):
        raise HTTPException(status_code=400, detail="Only active or enrollment_closed batches can be edited")

    updates = {}
    if "start_date" in body:
        updates["start_date"] = body["start_date"]
    if "enrollment_deadline" in body:
        updates["enrollment_deadline"] = body["enrollment_deadline"]
    if "instructor" in body:
        if not isinstance(body["instructor"], dict):
            raise HTTPException(status_code=400, detail="instructor must be an object")
        current_instructor = data.get("instructor", {})
        current_instructor.update(body["instructor"])
        updates["instructor"] = current_instructor

    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    updates["updated_at"] = firestore.SERVER_TIMESTAMP
    doc_ref.update(updates)

    _invalidate_overrides_cache()
    return {"message": "Batch updated"}


@router.post("/courses/{slug}/batches/{batch_id}/close-enrollment")
def close_batch_enrollment(slug: str, batch_id: str, admin: dict = Depends(verify_jwt)):
    """Close enrollment for an active batch. Moves physical_docs_required enrollments back to in_waitlist."""
    if slug not in _COURSES_BY_SLUG:
        raise HTTPException(status_code=404, detail="Course not found")

    collection = "course_batches"
    doc_ref = db.collection(collection).document(batch_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Batch not found")

    data = doc.to_dict()
    if data.get("course_slug") != slug:
        raise HTTPException(status_code=400, detail="Batch does not belong to this course")
    if data.get("status") != "active":
        raise HTTPException(status_code=400, detail="Only active batches can have enrollment closed")

    # Update batch status
    doc_ref.update({
        "status": "enrollment_closed",
        "closed_enrollment_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })

    # Move physical_docs_required enrollments back to in_waitlist
    course_title = _COURSES_BY_SLUG[slug].title
    enrollment_collection = "pending_enrollment_application"
    affected_docs = (
        db.collection(enrollment_collection)
        .where("course", "==", course_title)
        .where("status", "==", "physical_docs_required")
        .stream()
    )

    admin_email = admin.get("sub", "unknown")
    now = datetime.now(timezone.utc).isoformat()
    reverted_count = 0

    for edoc in affected_docs:
        edata = edoc.to_dict()
        existing_changelog = edata.get("changelog", [])
        edoc.reference.update({
            "status": "in_waitlist",
            "updated_at": firestore.SERVER_TIMESTAMP,
            "changelog": existing_changelog + [{
                "field": "status",
                "oldValue": "physical_docs_required",
                "newValue": "in_waitlist",
                "updatedBy": admin_email,
                "updatedAt": now,
                "note": "Enrollment closed for batch — reverted to waitlist",
            }],
        })
        reverted_count += 1

    _invalidate_overrides_cache()
    return {
        "message": "Enrollment closed",
        "reverted_to_waitlist": reverted_count,
    }


@router.post("/courses/{slug}/batches/{batch_id}/close")
def close_batch(slug: str, batch_id: str, _admin: dict = Depends(verify_jwt)):
    """Close/complete a batch. Course reverts to TBA (no active batch)."""
    if slug not in _COURSES_BY_SLUG:
        raise HTTPException(status_code=404, detail="Course not found")

    collection = "course_batches"
    doc_ref = db.collection(collection).document(batch_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Batch not found")

    data = doc.to_dict()
    if data.get("course_slug") != slug:
        raise HTTPException(status_code=400, detail="Batch does not belong to this course")
    if data.get("status") not in ("active", "enrollment_closed"):
        raise HTTPException(status_code=400, detail="Only active or enrollment_closed batches can be closed")

    doc_ref.update({
        "status": "completed",
        "completed_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })

    _invalidate_overrides_cache()
    return {"message": "Batch closed. Course reverts to TBA."}


# ── Admin: batch history ──────────────────────────────────────────────


@router.get("/courses/{slug}/batches")
def get_course_batches(slug: str, _admin: dict = Depends(verify_jwt)):
    """Get batch history for a course from course_batches collection."""
    course = _COURSES_BY_SLUG.get(slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    overrides = _get_course_overrides()
    merged_course = _apply_overrides(course, overrides)

    # Get all batches for this course
    batch_collection = "course_batches"
    batch_docs = list(
        db.collection(batch_collection)
        .where("course_slug", "==", slug)
        .stream()
    )

    # Get completed enrollments for this course
    enrollment_collection = "pending_enrollment_application"
    enrollment_docs = list(
        db.collection(enrollment_collection)
        .where("course", "==", merged_course.title)
        .where("status", "==", "completed")
        .stream()
    )

    # Group enrollments by batch_id
    enrollments_by_batch = {}
    legacy_enrollments = []
    for edoc in enrollment_docs:
        edata = edoc.to_dict()
        created_at = edata.get("created_at")
        if created_at and hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()

        student_entry = {
            "enrollment_id": edoc.id,
            "firstName": edata.get("firstName", ""),
            "lastName": edata.get("lastName", ""),
            "email": edata.get("email", ""),
            "created_at": created_at,
        }

        bid = edata.get("batch_id")
        if bid:
            enrollments_by_batch.setdefault(bid, []).append(student_entry)
        else:
            legacy_enrollments.append(student_entry)

    # Build batch list sorted by created_at
    active_batch = None
    completed_batches = []
    for bdoc in batch_docs:
        bdata = bdoc.to_dict()
        created_at = bdata.get("created_at")
        if created_at and hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
        completed_at = bdata.get("completed_at")
        if completed_at and hasattr(completed_at, "isoformat"):
            completed_at = completed_at.isoformat()
        closed_enrollment_at = bdata.get("closed_enrollment_at")
        if closed_enrollment_at and hasattr(closed_enrollment_at, "isoformat"):
            closed_enrollment_at = closed_enrollment_at.isoformat()

        students = enrollments_by_batch.get(bdoc.id, [])
        batch_entry = {
            "batch_id": bdoc.id,
            "status": bdata.get("status"),
            "start_date": bdata.get("start_date"),
            "enrollment_deadline": bdata.get("enrollment_deadline"),
            "instructor": bdata.get("instructor"),
            "student_count": len(students),
            "students": students,
            "created_at": created_at,
            "completed_at": completed_at,
            "closed_enrollment_at": closed_enrollment_at,
        }

        if bdata.get("status") in ("active", "enrollment_closed"):
            active_batch = batch_entry
        else:
            completed_batches.append(batch_entry)

    # Sort completed batches by created_at descending
    completed_batches.sort(key=lambda b: b.get("created_at") or "", reverse=True)

    # Number the completed batches (oldest = Batch 1)
    completed_batches_numbered = []
    for idx, batch in enumerate(reversed(completed_batches)):
        batch["batch_number"] = idx + 1
        batch["batch_label"] = f"Batch {idx + 1}"
        completed_batches_numbered.append(batch)
    completed_batches_numbered.reverse()

    # Add legacy enrollments as a special batch if any exist
    if legacy_enrollments:
        completed_batches_numbered.append({
            "batch_id": None,
            "batch_number": 0,
            "batch_label": "Legacy (Pre-tracking)",
            "status": "completed",
            "start_date": None,
            "enrollment_deadline": None,
            "instructor": None,
            "student_count": len(legacy_enrollments),
            "students": legacy_enrollments,
            "created_at": None,
            "completed_at": None,
            "closed_enrollment_at": None,
        })

    total_students = sum(len(enrollments_by_batch.get(bdoc.id, [])) for bdoc in batch_docs) + len(legacy_enrollments)

    return {
        "course": merged_course.model_dump(),
        "active_batch": active_batch,
        "batches": completed_batches_numbered,
        "total_students": total_students,
        "total_batches": len(batch_docs),
    }
