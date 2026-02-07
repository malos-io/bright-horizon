# Project: Training Center (Bright Horizons Institute Inc.)

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Always Vue 3 (Composition API, `<script setup>`)
- **Database**: Firestore (default database)

## Architecture
- `backend/` — FastAPI backend (shared by all frontends)
- `frontend-public/` — Public-facing website
- `frontend-admin/` — Admin portal
- `frontend-student/` — Student portal

## Database Collection Naming
Environment-based prefixes for Firestore collections:

| Environment | Collection Pattern       | Example              |
|-------------|--------------------------|----------------------|
| Dev         | `dev_{collection_name}`  | `dev_courses`        |
| Staging     | `staging_{collection_name}` | `staging_courses` |
| Production  | `{collection_name}`     | `courses`            |

All environments use the **(default)** Firestore database.

## Theme Colors
- Primary Blue: `#1a5fa4`
- Accent Orange: `#e8872a`
- Gradient: `linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%)`

## Deployment
- **Docker Compose (dev)**: `docker compose -f docker-compose.dev.yml up --build`
- **Docker Compose (prod)**: `docker compose up --build`
- **Cloud Build (staging)**: `cloudbuild-staging.yaml` deploys to Cloud Run (asia-southeast1)
