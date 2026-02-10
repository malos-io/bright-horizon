import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/address", tags=["address"])

# Load data once at module level
_data_dir = Path(__file__).parent.parent / "data"

with open(_data_dir / "barangays.json", encoding="utf-8") as f:
    _barangays = json.load(f)


@router.get("/barangays/{city_name}")
def get_barangays_by_path(city_name: str):
    """Return barangay list for a given city/municipality (path param)."""
    barangays = _barangays.get(city_name)
    if barangays is None:
        raise HTTPException(status_code=404, detail=f"No barangays found for '{city_name}'")
    return JSONResponse(
        content=barangays,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/barangays")
def get_barangays(city: str = Query(...)):
    """Return barangay list for a given city/municipality (query param)."""
    barangays = _barangays.get(city)
    if barangays is None:
        raise HTTPException(status_code=404, detail=f"No barangays found for '{city}'")
    return JSONResponse(
        content=barangays,
        headers={"Cache-Control": "public, max-age=86400"},
    )
