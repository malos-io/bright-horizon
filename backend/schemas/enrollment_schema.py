from pydantic import BaseModel
from typing import Optional, List


class EnrollmentApplication(BaseModel):
    # Section 2 - Manpower Profile
    lastName: str
    firstName: str
    middleName: Optional[str] = ""
    street: Optional[str] = ""
    barangay: Optional[str] = ""
    district: Optional[str] = ""
    city: Optional[str] = ""
    province: Optional[str] = ""
    region: Optional[str] = ""
    email: str
    contactNo: str
    nationality: Optional[str] = "Filipino"

    # Section 3 - Personal Information
    sex: Optional[str] = ""
    civilStatus: Optional[str] = ""
    employmentStatus: Optional[str] = ""
    birthMonth: Optional[str] = ""
    birthDay: Optional[str] = ""
    birthYear: Optional[str] = ""
    birthplaceCity: Optional[str] = ""
    birthplaceProvince: Optional[str] = ""
    birthplaceRegion: Optional[str] = ""
    educationalAttainment: Optional[str] = ""

    # Section 4 - Learner/Trainee/Student (Clients) Classification
    learnerClassification: Optional[List[str]] = []
    classificationOther: Optional[str] = ""

    # Section 5 - NCAE / YP4SC
    ncaeTaken: Optional[bool] = False
    ncaeWhere: Optional[str] = ""
    ncaeWhen: Optional[str] = ""

    # Section 6 - Course/Qualification
    course: str

    # Section 7 - Certification
    certificationAgreed: Optional[bool] = False

    # Section 8 - Scholarship
    applyScholarship: Optional[bool] = False
    scholarshipVoucher: Optional[str] = ""
    scholarshipPackage: Optional[str] = ""
    scholarshipCourse: Optional[str] = ""
