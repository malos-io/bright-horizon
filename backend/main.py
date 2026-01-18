from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Training Center API")

# CORS middleware for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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


# Sample Data
INSTRUCTORS = {
    "maria_santos": Instructor(
        name="Maria Santos",
        title="Senior Hospitality Trainer",
        bio="15+ years of experience in hotel management and hospitality training. Former Executive Housekeeper at major international hotel chains.",
        image="/images/instructors/maria.jpg"
    ),
    "juan_dela_cruz": Instructor(
        name="Juan Dela Cruz",
        title="Culinary Arts Director",
        bio="Award-winning chef with experience in 5-star restaurants across Asia and Europe.",
        image="/images/instructors/juan.jpg"
    ),
}

COURSES = [
    Course(
        id="1",
        slug="housekeeping",
        title="Professional Housekeeping",
        short_description="Master the art of professional housekeeping and room attendant services for hotels and hospitality industry.",
        description="""This comprehensive Professional Housekeeping course prepares you for a rewarding career in the hospitality industry.

You will learn industry-standard cleaning techniques, room preparation, guest service excellence, and hotel operations management. Our hands-on training approach ensures you gain practical skills that employers are looking for.

Whether you're starting fresh or upgrading your skills, this TESDA-accredited program will give you the competitive edge in the job market. Our graduates are employed in top hotels locally and internationally.""",
        image="/images/courses/housekeeping.jpg",
        duration_weeks=4,
        total_hours=160,
        price=15000,
        discounted_price=12500,
        category="Hospitality",
        level="Beginner",
        certification="TESDA NC II Certified",
        class_size=20,
        start_dates=["February 1, 2026", "March 1, 2026", "April 1, 2026"],
        schedule=[
            CourseSchedule(day="Monday - Friday", time="8:00 AM - 5:00 PM", duration="8 hours/day"),
            CourseSchedule(day="Saturday (Optional)", time="9:00 AM - 12:00 PM", duration="3 hours"),
        ],
        modules=[
            CourseModule(
                title="Introduction to Housekeeping",
                description="Overview of housekeeping department, roles and responsibilities, industry standards",
                duration_hours=16
            ),
            CourseModule(
                title="Cleaning Equipment & Supplies",
                description="Proper use of cleaning equipment, chemicals, safety protocols, and inventory management",
                duration_hours=24
            ),
            CourseModule(
                title="Room Cleaning & Bed Making",
                description="Step-by-step room cleaning procedures, bed making techniques, turndown service",
                duration_hours=40
            ),
            CourseModule(
                title="Laundry & Linen Management",
                description="Laundry operations, linen handling, stain removal, fabric care",
                duration_hours=24
            ),
            CourseModule(
                title="Public Area Cleaning",
                description="Lobby, hallways, restrooms, and common area maintenance",
                duration_hours=24
            ),
            CourseModule(
                title="Guest Services & Communication",
                description="Professional communication, handling guest requests, complaint resolution",
                duration_hours=16
            ),
            CourseModule(
                title="Practical Assessment & Review",
                description="Hands-on assessment, TESDA NC II preparation, mock examinations",
                duration_hours=16
            ),
        ],
        requirements=[
            "At least 18 years old",
            "High school graduate or equivalent",
            "Good physical health",
            "Basic English communication skills",
            "Valid government ID",
        ],
        what_you_learn=[
            "Industry-standard cleaning techniques and procedures",
            "Proper use of housekeeping equipment and chemicals",
            "Professional bed making and room setup",
            "Guest service excellence and communication skills",
            "Health and safety protocols in hospitality",
            "Time management and work efficiency",
            "Laundry operations and linen management",
        ],
        career_opportunities=[
            "Room Attendant / Housekeeper",
            "Housekeeping Supervisor",
            "Laundry Attendant",
            "Public Area Cleaner",
            "Executive Housekeeper",
            "Cruise Ship Housekeeping Staff",
            "Hospital / Healthcare Facility Housekeeper",
        ],
        instructor=INSTRUCTORS["maria_santos"],
        enrolled_count=1250,
        rating=4.8,
        reviews_count=342
    ),
    Course(
        id="2",
        slug="food-and-beverage",
        title="Food & Beverage Services",
        short_description="Learn professional food service, bartending, and restaurant operations for the hospitality industry.",
        description="""Become a skilled Food & Beverage professional with our comprehensive training program. Learn restaurant service, bartending, and hospitality management from industry experts.""",
        image="/images/courses/fnb.jpg",
        duration_weeks=6,
        total_hours=240,
        price=18000,
        discounted_price=15000,
        category="Hospitality",
        level="Beginner",
        certification="TESDA NC II Certified",
        class_size=20,
        start_dates=["February 15, 2026", "March 15, 2026"],
        schedule=[
            CourseSchedule(day="Monday - Friday", time="8:00 AM - 5:00 PM", duration="8 hours/day"),
        ],
        modules=[
            CourseModule(title="Introduction to F&B Service", description="Industry overview and service standards", duration_hours=24),
            CourseModule(title="Table Service & Setup", description="Table setting, service styles, etiquette", duration_hours=40),
            CourseModule(title="Bartending Basics", description="Drink preparation, bar operations", duration_hours=40),
            CourseModule(title="Kitchen Coordination", description="Order taking, kitchen communication", duration_hours=24),
            CourseModule(title="Customer Service Excellence", description="Guest handling, complaint resolution", duration_hours=24),
        ],
        requirements=["At least 18 years old", "High school graduate", "Good communication skills"],
        what_you_learn=["Professional table service", "Bartending and mixology", "Customer service excellence"],
        career_opportunities=["Waiter/Waitress", "Bartender", "Restaurant Supervisor", "F&B Manager"],
        instructor=INSTRUCTORS["juan_dela_cruz"],
        enrolled_count=980,
        rating=4.7,
        reviews_count=256
    ),
    Course(
        id="3",
        slug="front-office",
        title="Front Office Services",
        short_description="Master hotel front desk operations, reservations, and guest relations management.",
        description="""Develop essential front office skills for hotels and hospitality establishments. Learn reservation systems, guest check-in/out procedures, and professional communication.""",
        image="/images/courses/frontoffice.jpg",
        duration_weeks=4,
        total_hours=160,
        price=14000,
        discounted_price=None,
        category="Hospitality",
        level="Beginner",
        certification="TESDA NC II Certified",
        class_size=15,
        start_dates=["February 10, 2026", "March 10, 2026"],
        schedule=[
            CourseSchedule(day="Monday - Friday", time="8:00 AM - 5:00 PM", duration="8 hours/day"),
        ],
        modules=[
            CourseModule(title="Front Office Operations", description="Department overview and procedures", duration_hours=32),
            CourseModule(title="Reservation Systems", description="Booking systems, room allocation", duration_hours=32),
            CourseModule(title="Guest Relations", description="Check-in/out, guest services", duration_hours=32),
            CourseModule(title="Communication Skills", description="Professional phone and email handling", duration_hours=24),
        ],
        requirements=["At least 18 years old", "High school graduate", "Computer literate"],
        what_you_learn=["Hotel reservation systems", "Guest check-in/out procedures", "Professional communication"],
        career_opportunities=["Front Desk Agent", "Reservations Officer", "Guest Relations Officer"],
        instructor=INSTRUCTORS["maria_santos"],
        enrolled_count=720,
        rating=4.6,
        reviews_count=189
    ),
    Course(
        id="4",
        slug="caregiving",
        title="Caregiving",
        short_description="Comprehensive caregiver training for elderly care, patient assistance, and healthcare support.",
        description="""Prepare for a fulfilling career in healthcare with our TESDA-accredited Caregiving program. Learn patient care, vital signs monitoring, and compassionate caregiving.""",
        image="/images/courses/caregiving.jpg",
        duration_weeks=8,
        total_hours=320,
        price=25000,
        discounted_price=22000,
        category="Healthcare",
        level="Beginner",
        certification="TESDA NC II Certified",
        class_size=25,
        start_dates=["February 1, 2026", "April 1, 2026"],
        schedule=[
            CourseSchedule(day="Monday - Saturday", time="8:00 AM - 5:00 PM", duration="8 hours/day"),
        ],
        modules=[
            CourseModule(title="Fundamentals of Caregiving", description="Basic patient care principles", duration_hours=40),
            CourseModule(title="Vital Signs & Health Monitoring", description="Taking vital signs, health assessment", duration_hours=40),
            CourseModule(title="Elderly Care", description="Geriatric care, mobility assistance", duration_hours=60),
            CourseModule(title="First Aid & Emergency Response", description="Emergency procedures, CPR", duration_hours=40),
            CourseModule(title="Clinical Practicum", description="Hands-on hospital/facility training", duration_hours=80),
        ],
        requirements=["At least 18 years old", "High school graduate", "Good physical health", "No criminal record"],
        what_you_learn=["Patient care fundamentals", "Vital signs monitoring", "Emergency response", "Elderly care techniques"],
        career_opportunities=["Private Caregiver", "Hospital Aide", "Nursing Home Staff", "Home Health Aide"],
        instructor=INSTRUCTORS["maria_santos"],
        enrolled_count=1580,
        rating=4.9,
        reviews_count=425
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


@app.get("/api/courses/category/{category}", response_model=list[Course])
def get_courses_by_category(category: str):
    return [course for course in COURSES if course.category.lower() == category.lower()]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
