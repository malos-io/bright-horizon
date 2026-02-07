from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import course_router, sponsor_router, enrollment_router

app = FastAPI(title="Training Center API")

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


@app.get("/")
def read_root():
    return {"message": "Welcome to Training Center API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
