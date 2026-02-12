# Local Development with Emulators

Your dev environment now uses **local emulators** instead of connecting to cloud Firestore/Storage!

## What's Running

When you run `docker-compose -f docker-compose.dev.yml up`, you get:

```
✅ Firestore Emulator (port 8080) - Local database
✅ Storage Emulator (port 9199) - Local file storage
✅ Auth Emulator (port 9099) - Local authentication
✅ Emulator UI (port 4000) - Web interface to view/manage data
✅ Backend (port 8000) - Your FastAPI app
✅ Frontend Admin (port 5174) - Vue admin app
✅ Frontend Public (port 5173) - Vue public app
✅ Frontend Student (port 5175) - Vue student app
```

## Benefits

- ✅ **Completely offline** - No cloud connection needed
- ✅ **Free** - No Firestore/Storage costs for dev
- ✅ **Fast** - Localhost = instant queries
- ✅ **Isolated** - Your data doesn't mix with staging
- ✅ **Safe** - Can't accidentally break staging
- ✅ **Fresh start** - Clean database on every restart

## How to Use

### Start Development Environment

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Or in detached mode
docker-compose -f docker-compose.dev.yml up -d
```

### View Emulator UI

Open in browser: http://localhost:4000

You'll see:
- Firestore data (collections, documents)
- Storage files (uploaded PDFs, images)
- Auth users (if using Firebase Auth)
- Logs from all emulators

### Access Your Apps

- Admin Frontend: http://localhost:5174
- Public Frontend: http://localhost:5173
- Student Frontend: http://localhost:5175
- Backend API: http://localhost:8000
- Emulator UI: http://localhost:4000

### Stop Development Environment

```bash
docker-compose -f docker-compose.dev.yml down
```

**Note:** This will delete all emulator data (that's the point!)

## Data Persistence

### Default: Data is Lost on Restart

```
Stop containers → All Firestore data is lost
Restart → Fresh empty database

This is GOOD for development!
```

### Firestore Data

- Stored in **memory** (RAM)
- Lost when you stop containers
- Fresh start every time

### Storage Files

- Stored in `./emulator-data/storage/`
- **Persisted** to disk
- Survives restarts

## Seeding Test Data

To populate test data on startup, create a seed script:

```python
# backend/seed_data.py
from reusable_components.firebase import db, get_collection_name

def seed():
    # Add test users
    db.collection(get_collection_name('users')).add({
        'name': 'Test User',
        'email': 'test@example.com'
    })
    
    # Add test courses
    db.collection(get_collection_name('courses')).add({
        'title': 'Vue.js Basics',
        'duration': 40
    })
    
    print("✅ Seed data created!")

if __name__ == "__main__":
    seed()
```

Run it:
```bash
docker-compose -f docker-compose.dev.yml exec backend python seed_data.py
```

## Troubleshooting

### Emulator won't start

```bash
# Check if ports are in use
lsof -i :8080  # Firestore
lsof -i :9199  # Storage
lsof -i :4000  # UI

# Kill processes if needed
kill -9 <PID>
```

### Backend can't connect to emulator

Check environment variables are set:
```bash
docker-compose -f docker-compose.dev.yml exec backend env | grep EMULATOR

# Should show:
# FIRESTORE_EMULATOR_HOST=firestore-emulator:8080
# FIREBASE_STORAGE_EMULATOR_HOST=firebase-emulators:9199
```

### Data persists when it shouldn't

Clear volumes:
```bash
docker-compose -f docker-compose.dev.yml down -v
```

## Switching Between Emulator and Cloud

### Use Emulator (Dev):
```bash
docker-compose -f docker-compose.dev.yml up
```
Backend connects to localhost emulators

### Use Cloud (Testing):
```bash
# Remove emulator env vars from docker-compose.dev.yml
# Backend will connect to brighthii project in cloud
```

## What's Different from Cloud

| Feature | Emulator | Cloud |
|---------|----------|-------|
| **Data** | Temporary | Permanent |
| **Cost** | Free | Costs money |
| **Speed** | Instant | Network latency |
| **Offline** | Works | Need internet |
| **Shared** | Just you | Whole team (if same project) |

## Next Steps

1. Start containers: `docker-compose -f docker-compose.dev.yml up`
2. Open Emulator UI: http://localhost:4000
3. Open Admin: http://localhost:5174
4. Develop features locally!
5. When ready, deploy to staging (connects to cloud)

---

**Questions?** Check the main README or ask your team!
