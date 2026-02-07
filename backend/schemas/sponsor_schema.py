from pydantic import BaseModel
from typing import Optional


class Sponsor(BaseModel):
    id: str
    name: str
    title: str
    position: Optional[str] = None
    image: str
    scholars_sponsored: int
    message: Optional[str] = None
