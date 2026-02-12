from pydantic import BaseModel
from typing import Optional, List


class InstructorApplication(BaseModel):
    firstName: str
    lastName: str
    email: str
    contactNo: str
    coursesInterested: List[str] = []
    otherCourses: Optional[str] = ""
