# Training Center Web Application

A modern training center website built with FastAPI (backend) and Vue.js (frontend), similar to Blend Academy and Udemy.

## Features

- Homepage with hero section, course listings, and features
- Course catalog with category filtering
- Detailed course pages with:
  - Course overview and description
  - Curriculum/modules breakdown
  - Requirements and career opportunities
  - Instructor information
  - Pricing and enrollment options
  - Schedule and upcoming batch dates
- Responsive design for mobile and desktop
- TESDA-accredited courses for Philippine market

## Project Structure

```
training-center/
├── backend/
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
└── frontend/
    ├── src/
    │   ├── components/   # Vue components (Navbar, Footer, CourseCard)
    │   ├── views/        # Page views (Home, Courses, CourseDetail)
    │   ├── router/       # Vue Router configuration
    │   ├── services/     # API service layer
    │   ├── App.vue       # Root component
    │   └── main.js       # Entry point
    └── index.html
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd training-center/backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd training-center/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## API Endpoints

- `GET /api/courses` - Get all courses
- `GET /api/courses/{slug}` - Get course by slug (e.g., `/api/courses/housekeeping`)
- `GET /api/categories` - Get all course categories
- `GET /api/courses/category/{category}` - Get courses by category

## Available Courses

1. **Professional Housekeeping** (`/housekeeping`)
   - 4 weeks duration, 160 hours
   - TESDA NC II Certified

2. **Food & Beverage Services** (`/food-and-beverage`)
   - 6 weeks duration, 240 hours
   - TESDA NC II Certified

3. **Front Office Services** (`/front-office`)
   - 4 weeks duration, 160 hours
   - TESDA NC II Certified

4. **Caregiving** (`/caregiving`)
   - 8 weeks duration, 320 hours
   - TESDA NC II Certified

## Docker Deployment

### Development Mode (with Hot Reload)

For development with hot reload on both frontend and backend:

```bash
cd training-center
docker-compose -f docker-compose.dev.yml up --build
```

This will:
- Run FastAPI with `--reload` flag (auto-restarts on code changes)
- Run Vite dev server with HMR (Hot Module Replacement)
- Mount source code as volumes for live updates
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

Edit any file in `backend/` or `frontend/src/` and see changes instantly!

### Production Mode

For production deployment with Nginx:

```bash
cd training-center
docker-compose up --build
```

This will:
- Build the FastAPI backend container
- Build the Vue.js frontend and serve it via Nginx
- Configure Nginx as a reverse proxy for the API
- Expose the application on port 80

Access the application at `http://localhost`

### Docker Architecture

```
┌─────────────────────────────────────────────┐
│                  Nginx                       │
│              (Port 80)                       │
│                                             │
│   ┌─────────────┐    ┌─────────────────┐   │
│   │   Static    │    │  Reverse Proxy  │   │
│   │   Files     │    │    /api/*       │   │
│   │   (Vue.js)  │    │       ↓         │   │
│   └─────────────┘    └─────────────────┘   │
│                              │              │
└──────────────────────────────│──────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │   (Port 8000)   │
                    └─────────────────┘
```

### Docker Commands

```bash
# Build and start containers
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build frontend
docker-compose build backend
```

## Tech Stack

- **Backend**: FastAPI, Pydantic, Uvicorn
- **Frontend**: Vue.js 3, Vue Router, Axios
- **Styling**: Custom CSS with modern design
- **Build Tool**: Vite
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (reverse proxy + static files)

## Customization

To add more courses, edit the `COURSES` list in `backend/main.py`. Each course requires:
- Basic info (title, description, slug)
- Duration and pricing
- Modules/curriculum
- Requirements and career opportunities
- Instructor information
- Schedule and start dates
