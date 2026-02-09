from dotenv import load_dotenv

# Load .env for local dev (no-op if file doesn't exist, e.g. on Cloud Run)
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import course_router, sponsor_router, enrollment_router, zoho_router, email_router, staff_router, pdf_router, address_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Training Center API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
# Allow any *.brighthii.com subdomain, plus localhost for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_origin_regex=r"https://.*\.brighthii\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(course_router.router)
app.include_router(sponsor_router.router)
app.include_router(enrollment_router.router)
app.include_router(zoho_router.router)
app.include_router(email_router.router)
app.include_router(staff_router.router)
app.include_router(pdf_router.router)
app.include_router(address_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Training Center API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
