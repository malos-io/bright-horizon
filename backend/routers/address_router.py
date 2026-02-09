import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/address", tags=["address"])

# Load data once at module level
_data_dir = Path(__file__).parent.parent / "data"

with open(_data_dir / "barangays.json", encoding="utf-8") as f:
    _barangays = json.load(f)


@router.get("/barangays/{city_name}")
def get_barangays(city_name: str):
    """Return barangay list for a given city/municipality."""
    barangays = _barangays.get(city_name)
    if barangays is None:
        raise HTTPException(status_code=404, detail=f"No barangays found for '{city_name}'")
    return JSONResponse(
        content=barangays,
        headers={"Cache-Control": "public, max-age=86400"},
    )
