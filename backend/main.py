import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Training Center API")

# CORS middleware for Vue.js frontend
# Allow origins from environment variable (comma-separated) or default to localhost
default_origins = ["http://localhost:5173", "http://localhost:3000"]
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else default_origins
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class CourseModule(BaseModel):
    title: str
    description: str
    duration_hours: int


class CourseSchedule(BaseModel):
    day: str
    time: str
    duration: str


class Instructor(BaseModel):
    name: str
    title: str
    bio: str
    image: str


class Course(BaseModel):
    id: str
    slug: str
    title: str
    short_description: str
    description: str
    image: str
    duration_weeks: int
    total_hours: int
    price: float
    discounted_price: Optional[float] = None
    category: str
    level: str
    certification: str
    class_size: int
    start_dates: list[str]
    schedule: list[CourseSchedule]
    modules: list[CourseModule]
    requirements: list[str]
    what_you_learn: list[str]
    career_opportunities: list[str]
    instructor: Instructor
    enrolled_count: int
    rating: float
    reviews_count: int


class Sponsor(BaseModel):
    id: str
    name: str
    title: str
    position: Optional[str] = None
    image: str
    scholars_sponsored: int
    message: Optional[str] = None


# Sponsors
SPONSORS = [
    Sponsor(
        id="1",
        name="Hon. Juan Dela Cruz",
        title="City Councilor",
        position="District 1, Manila",
        image="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop",
        scholars_sponsored=25,
        message="Education is the key to progress. I am proud to support our youth in gaining valuable skills."
    ),
    Sponsor(
        id="2",
        name="Hon. Maria Santos",
        title="Barangay Captain",
        position="Barangay 123, Manila",
        image="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop",
        scholars_sponsored=15,
        message="Empowering our community through skills training creates opportunities for everyone."
    ),
    Sponsor(
        id="3",
        name="Hon. Roberto Reyes",
        title="Provincial Board Member",
        position="3rd District",
        image="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop",
        scholars_sponsored=30,
        message="Investing in our people's skills is investing in our province's future."
    ),
]


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
            "Basic computer literacy",
            "Basic math skills",
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
            "Can communicate in basic English (oral and written)",
            "Good interpersonal skills",
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


# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to Training Center API"}


@app.get("/api/courses", response_model=list[Course])
def get_courses():
    return COURSES


@app.get("/api/courses/{slug}", response_model=Course)
def get_course(slug: str):
    for course in COURSES:
        if course.slug == slug:
            return course
    return {"error": "Course not found"}


@app.get("/api/categories")
def get_categories():
    categories = list(set(course.category for course in COURSES))
    return categories


@app.get("/api/sponsors", response_model=list[Sponsor])
def get_sponsors():
    return SPONSORS


@app.get("/api/courses/category/{category}", response_model=list[Course])
def get_courses_by_category(category: str):
    return [course for course in COURSES if course.category.lower() == category.lower()]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
