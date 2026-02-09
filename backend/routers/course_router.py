from fastapi import APIRouter
from schemas.course_schema import Course, CourseModule, CourseSchedule, Instructor

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
        total_hours=240,
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
                duration_hours=24
            ),
            CourseModule(
                title="Journalizing Transactions",
                description="Logging and recording business transactions in an accounting journal, best practices and procedures",
                duration_hours=48
            ),
            CourseModule(
                title="Posting Transactions",
                description="Posting transactions manually and digitally, foundational knowledge on format and procedures",
                duration_hours=48
            ),
            CourseModule(
                title="Preparing Trial Balance",
                description="Listing accounts, transferring and summarizing trial balances from a ledger, key considerations",
                duration_hours=40
            ),
            CourseModule(
                title="Preparing Financial Reports",
                description="Preparing financial reports manually, guidance on report preparation procedures",
                duration_hours=48
            ),
            CourseModule(
                title="Reviewing Internal Control System",
                description="Reviewing and determining extent of compliance with a firm's internal control manual, effectiveness assessment",
                duration_hours=32
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
        duration_weeks=3,
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
]


@router.get("/courses", response_model=list[Course])
def get_courses():
    return COURSES


@router.get("/courses/{slug}", response_model=Course)
def get_course(slug: str):
    for course in COURSES:
        if course.slug == slug:
            return course
    return {"error": "Course not found"}


@router.get("/categories")
def get_categories():
    categories = list(set(course.category for course in COURSES))
    return categories


@router.get("/courses/category/{category}", response_model=list[Course])
def get_courses_by_category(category: str):
    return [course for course in COURSES if course.category.lower() == category.lower()]
