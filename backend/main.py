import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import course_router, sponsor_router, enrollment_router

app = FastAPI(title="Training Center API")

# CORS middleware for Vue.js frontend
# Allow origins from environment variable (comma-separated) or default to localhost
default_origins = ["http://localhost:5173", "http://localhost:3000"]
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else default_origins
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
