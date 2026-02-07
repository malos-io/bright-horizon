from fastapi import APIRouter
from schemas.sponsor_schema import Sponsor

router = APIRouter(prefix="/api", tags=["sponsors"])

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


@router.get("/sponsors", response_model=list[Sponsor])
def get_sponsors():
    return SPONSORS
