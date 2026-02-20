import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/address", tags=["address"])

# Load data once at module level
_data_dir = Path(__file__).parent.parent / "data"

with open(_data_dir / "philippines_location.json", encoding="utf-8") as f:
    _locations = json.load(f)

with open(_data_dir / "districts.json", encoding="utf-8") as f:
    _districts = json.load(f)

# Region IX only (for mailing address)
_local_regions = [
    "Region IX (Zamboanga Peninsula)",
]


@router.get("/regions")
def get_regions(all: bool = Query(False)):
    """Return list of region names. Use ?all=true for all 17 regions."""
    regions = list(_locations.keys()) if all else _local_regions
    return JSONResponse(
        content=regions,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/provinces")
def get_provinces(region: str = Query(...)):
    """Return list of province names for a given region."""
    region_data = _locations.get(region)
    if region_data is None:
        raise HTTPException(status_code=404, detail=f"Region not found: '{region}'")
    return JSONResponse(
        content=list(region_data.keys()),
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/cities")
def get_cities(region: str = Query(...), province: str = Query(...)):
    """Return list of cities with optional district info."""
    region_data = _locations.get(region)
    if region_data is None:
        raise HTTPException(status_code=404, detail=f"Region not found: '{region}'")
    province_data = region_data.get(province)
    if province_data is None:
        raise HTTPException(status_code=404, detail=f"Province not found: '{province}'")

    district_map = _districts.get(province, {})
    cities = [
        {"name": city, "district": district_map.get(city, "")}
        for city in province_data.keys()
    ]
    return JSONResponse(
        content=cities,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/barangays")
def get_barangays(
    city: str = Query(...),
    region: Optional[str] = Query(None),
    province: Optional[str] = Query(None),
):
    """Return barangay list for a given city. Optionally scope by region/province."""
    # If region and province given, do precise lookup
    if region and province:
        region_data = _locations.get(region, {})
        province_data = region_data.get(province, {})
        barangays = province_data.get(city)
        if barangays is not None:
            return JSONResponse(
                content=barangays,
                headers={"Cache-Control": "public, max-age=86400"},
            )

    # Fallback: search all regions/provinces for the city
    for r_data in _locations.values():
        for p_data in r_data.values():
            if city in p_data:
                return JSONResponse(
                    content=p_data[city],
                    headers={"Cache-Control": "public, max-age=86400"},
                )

    raise HTTPException(status_code=404, detail=f"No barangays found for '{city}'")


@router.get("/barangays/{city_name}")
def get_barangays_by_path(city_name: str):
    """Return barangay list for a given city/municipality (path param)."""
    for r_data in _locations.values():
        for p_data in r_data.values():
            if city_name in p_data:
                return JSONResponse(
                    content=p_data[city_name],
                    headers={"Cache-Control": "public, max-age=86400"},
                )

    raise HTTPException(status_code=404, detail=f"No barangays found for '{city_name}'")
