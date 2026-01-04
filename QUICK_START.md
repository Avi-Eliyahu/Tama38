# TAMA38 Phase 1 - Quick Start Guide

## Prerequisites

- Docker Desktop for Windows
- Git

## Setup Steps

### 1. Start Services

```powershell
docker-compose up -d
```

Wait for all services to start (about 30 seconds).

### 2. Run Database Migrations

```powershell
docker-compose exec backend alembic upgrade head
```

### 3. Create Admin User

```powershell
docker-compose exec backend python scripts/create_admin.py
```

This creates:
- Email: `admin@tama38.local`
- Password: `Admin123!@#`

### 4. Create Test Users (Optional)

```powershell
docker-compose exec backend python scripts/create_test_users.py
```

This creates test users for each role:
- `super_admin@test.com` / `Test123!@#`
- `project_manager@test.com` / `Test123!@#`
- `agent1@test.com` / `Test123!@#`
- `agent2@test.com` / `Test123!@#`
- `tenant1@test.com` / `Test123!@#`

## Access Points

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health
- **Database:** localhost:5432 (user: postgres, password: postgres)

## Testing

### Test Infrastructure

```powershell
# On Linux/Mac/Git Bash
./scripts/test_infrastructure.sh

# On Windows PowerShell (if WSL available)
wsl bash scripts/test_infrastructure.sh
```

### Test API Endpoints

1. **Login:**
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"admin@tama38.local","password":"Admin123!@#"}'
$token = $response.access_token
```

2. **Get Current User:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Method GET `
  -Headers @{Authorization="Bearer $token"}
```

3. **Create Project:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/projects" `
  -Method POST `
  -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
  -Body '{
    "project_name": "Test Project",
    "project_code": "TEST001",
    "project_type": "TAMA38_1",
    "required_majority_percent": 75.0,
    "critical_threshold_percent": 50.0,
    "majority_calc_type": "HEADCOUNT"
  }'
```

### View Logs

```powershell
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# All logs
docker-compose logs

# Follow logs
docker-compose logs -f backend
```

## Troubleshooting

### Services won't start
```powershell
# Check service status
docker-compose ps

# View logs
docker-compose logs

# Restart services
docker-compose restart
```

### Database connection errors
```powershell
# Check database is running
docker-compose ps database

# Restart database
docker-compose restart database

# Check database logs
docker-compose logs database
```

### Port already in use
- Change ports in `docker-compose.yml` if 3000, 8000, or 5432 are already in use

### Migration errors
```powershell
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## Next Steps

1. Test the API using the Swagger docs at http://localhost:8000/docs
2. Test the frontend login at http://localhost:3000
3. Run the E2E test script: `./scripts/e2e_test.sh` (Linux/Mac) or use PowerShell equivalent
4. Review the implementation status: `docs/IMPLEMENTATION_STATUS.md`

## Development

### Backend Development
```powershell
cd backend
# Install dependencies locally (optional)
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload
```

### Frontend Development
```powershell
cd frontend
npm install
npm run dev
```

## API Testing with curl (Git Bash)

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tama38.local","password":"Admin123!@#"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Get current user
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

