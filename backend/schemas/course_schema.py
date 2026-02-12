from pydantic import BaseModel
from typing import Optional


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
    enrollment_deadline: Optional[str] = None
    schedule: list[CourseSchedule]
    modules: list[CourseModule]
    requirements: list[str]
    what_you_learn: list[str]
    career_opportunities: list[str]
    instructor: Instructor
    enrolled_count: int
    rating: float
    reviews_count: int
    is_coming_soon: bool = False
