from pydantic import BaseModel
from typing import Optional


class EnrollmentApplication(BaseModel):
    fullName: str
    email: str
    phone: str
    course: str
    message: Optional[str] = ""
