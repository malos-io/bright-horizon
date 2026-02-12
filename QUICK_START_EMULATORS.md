# 🚀 Quick Start: Local Development with Emulators

## What Changed

Your dev environment now runs **100% locally** with emulators!

### Before (Connected to Cloud):
```
Dev → brighthii-creds.json → Cloud Firestore (staging data)
❌ Shared database with staging
❌ Costs money
❌ Need internet
```

### After (Local Emulators):
```
Dev → Emulators → Localhost (your data only)
✅ Completely isolated
✅ Free
✅ Works offline
```

---

## How to Start

### 1. Start Everything

```bash
cd /Users/206758220/Downloads/Tests/training-center

docker-compose -f docker-compose.dev.yml up
```

### 2. Wait for Services to Start

You'll see:
```
✅ firestore-emulator    | running on 0.0.0.0:8080
✅ firebase-emulators    | All emulators ready!
✅ backend               | Uvicorn running on http://0.0.0.0:8000
✅ frontend-admin        | VITE ready in 1234 ms
```

### 3. Open Emulator UI

**Browser:** http://localhost:4000

You'll see:
- **Firestore tab** - View collections (currently empty)
- **Storage tab** - View uploaded files
- **Auth tab** - View users
- **Logs tab** - See all emulator activity

---

## Test It Works

### Test 1: Check Backend Connects to Emulator

```bash
# In another terminal
docker-compose -f docker-compose.dev.yml exec backend python -c "
from reusable_components.firebase import db, get_collection_name
print('Adding test document...')
db.collection(get_collection_name('test')).add({'message': 'Hello from emulator!'})
print('✅ Success! Check http://localhost:4000')
"
```

**Then:**
1. Open http://localhost:4000
2. Click "Firestore" tab
3. You should see `dev_test` collection with your document!

### Test 2: Use the App

1. Open Admin: http://localhost:5174
2. Try to log in or create data
3. Check Emulator UI to see the data appear in real-time!

---

## Ports Reference

| Service | Port | URL |
|---------|------|-----|
| **Emulator UI** | 4000 | http://localhost:4000 |
| **Firestore Emulator** | 8080 | (Backend connects here) |
| **Storage Emulator** | 9199 | (Backend connects here) |
| **Backend API** | 8000 | http://localhost:8000 |
| **Frontend Admin** | 5174 | http://localhost:5174 |
| **Frontend Public** | 5173 | http://localhost:5173 |
| **Frontend Student** | 5175 | http://localhost:5175 |

---

## Common Commands

```bash
# Start (with logs)
docker-compose -f docker-compose.dev.yml up

# Start (detached/background)
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down

# Stop and clear all data
docker-compose -f docker-compose.dev.yml down -v

# Restart just backend
docker-compose -f docker-compose.dev.yml restart backend

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# View all logs
docker-compose -f docker-compose.dev.yml logs -f
```

---

## What's Included

### Emulator Services

1. **Firestore Emulator**
   - Local database
   - Port: 8080
   - Data: In-memory (lost on restart)

2. **Storage Emulator**
   - Local file storage
   - Port: 9199
   - Files: Saved to `./emulator-data/storage/`

3. **Auth Emulator**
   - Local authentication
   - Port: 9099
   - Fake users (for testing)

4. **Emulator UI**
   - Web interface
   - Port: 4000
   - View/manage all emulator data

---

## Files Changed

```
✅ docker-compose.dev.yml - Added emulator services
✅ emulator-data/ - Created emulator config folder
✅ emulator-data/firebase.json - Emulator configuration
✅ emulator-data/storage.rules - Storage security rules
✅ .gitignore - Added emulator temp files
✅ docker-compose.dev.yml.backup - Your original file (backup)
```

---

## Troubleshooting

### Can't access Emulator UI

```bash
# Check if running
docker ps | grep firebase-emulators

# Check logs
docker-compose -f docker-compose.dev.yml logs firebase-emulators

# Restart
docker-compose -f docker-compose.dev.yml restart firebase-emulators
```

### Backend still connects to cloud

```bash
# Check environment variables
docker-compose -f docker-compose.dev.yml exec backend env | grep FIRESTORE

# Should see:
# FIRESTORE_EMULATOR_HOST=firestore-emulator:8080

# If not, rebuild
docker-compose -f docker-compose.dev.yml up --build backend
```

### Port already in use

```bash
# Find what's using the port
lsof -i :4000

# Kill it
kill -9 <PID>

# Or change the port in docker-compose.dev.yml
```

---

## Next Steps

1. ✅ Start containers
2. ✅ Open Emulator UI (http://localhost:4000)
3. ✅ Test your app
4. 🎉 Develop with confidence!

**Remember:** 
- Dev data is temporary (lost on restart) ✅
- Staging data is in the cloud ✅
- You can't accidentally break staging anymore! 🎉

---

Need help? Check [EMULATOR_SETUP.md](./EMULATOR_SETUP.md) for detailed docs!
