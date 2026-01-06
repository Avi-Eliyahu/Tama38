# Installation Verification Script
# Verifies that TAMA38 is properly installed and running

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TAMA38 Installation Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$AllChecksPassed = $true

# Get project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Check 1: Docker is running
Write-Host "Check 1: Docker daemon..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Docker daemon is running" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker daemon is not running" -ForegroundColor Red
        $AllChecksPassed = $false
    }
} catch {
    Write-Host "  ✗ Docker is not available" -ForegroundColor Red
    $AllChecksPassed = $false
}

Write-Host ""

# Check 2: Containers are running
Write-Host "Check 2: Docker containers..." -ForegroundColor Yellow
$ExpectedContainers = @("tama38_database_prod", "tama38_backend_prod", "tama38_frontend_prod")
$RunningContainers = docker ps --format "{{.Names}}"

foreach ($Container in $ExpectedContainers) {
    if ($RunningContainers -match $Container) {
        $Status = docker ps --filter "name=$Container" --format "{{.Status}}"
        Write-Host "  ✓ $Container is running ($Status)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $Container is not running" -ForegroundColor Red
        $AllChecksPassed = $false
    }
}

Write-Host ""

# Check 3: Database connectivity
Write-Host "Check 3: Database connectivity..." -ForegroundColor Yellow
try {
    $DbCheck = docker-compose -f (Join-Path $ProjectRoot "docker-compose.prod.yml") exec -T database pg_isready -U postgres 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database is accepting connections" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Database is not accepting connections" -ForegroundColor Red
        $AllChecksPassed = $false
    }
} catch {
    Write-Host "  ✗ Could not check database connectivity" -ForegroundColor Red
    $AllChecksPassed = $false
}

Write-Host ""

# Check 4: Backend health endpoint
Write-Host "Check 4: Backend health endpoint..." -ForegroundColor Yellow
try {
    $HealthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($HealthResponse.StatusCode -eq 200) {
        Write-Host "  ✓ Backend is responding (HTTP $($HealthResponse.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Backend returned unexpected status: $($HealthResponse.StatusCode)" -ForegroundColor Red
        $AllChecksPassed = $false
    }
} catch {
    Write-Host "  ✗ Backend is not responding" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
    $AllChecksPassed = $false
}

Write-Host ""

# Check 5: Frontend accessibility
Write-Host "Check 5: Frontend accessibility..." -ForegroundColor Yellow
try {
    $FrontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($FrontendResponse.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend is accessible (HTTP $($FrontendResponse.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Frontend returned unexpected status: $($FrontendResponse.StatusCode)" -ForegroundColor Red
        $AllChecksPassed = $false
    }
} catch {
    Write-Host "  ✗ Frontend is not accessible" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
    $AllChecksPassed = $false
}

Write-Host ""

# Check 6: Backend API endpoint
Write-Host "Check 6: Backend API endpoint..." -ForegroundColor Yellow
try {
    $ApiResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($ApiResponse.StatusCode -eq 200 -or $ApiResponse.StatusCode -eq 401) {
        # 401 is OK - means API is working but requires auth
        Write-Host "  ✓ Backend API is responding" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Backend API returned status: $($ApiResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "  ✓ Backend API is responding (requires authentication)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Backend API is not responding" -ForegroundColor Red
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
        $AllChecksPassed = $false
    }
}

Write-Host ""

# Check 7: Admin user exists
Write-Host "Check 7: Admin user..." -ForegroundColor Yellow
try {
    $AdminCheck = docker-compose -f (Join-Path $ProjectRoot "docker-compose.prod.yml") exec -T backend python -c "from app.core.database import SessionLocal; from app.models.user import User; db = SessionLocal(); admin = db.query(User).filter(User.email == 'admin@tama38.local').first(); print('EXISTS' if admin else 'NOT_FOUND'); db.close()" 2>&1
    
    if ($AdminCheck -match "EXISTS") {
        Write-Host "  ✓ Admin user exists" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Admin user not found (may need to create)" -ForegroundColor Yellow
        Write-Host "    Run: docker-compose -f docker-compose.prod.yml exec backend python scripts/create_admin.py" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ⚠ Could not verify admin user" -ForegroundColor Yellow
}

Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
if ($AllChecksPassed) {
    Write-Host "✓ All critical checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "TAMA38 is installed and running correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the application:" -ForegroundColor Cyan
    Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
} else {
    Write-Host "✗ Some checks failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please review the errors above and:" -ForegroundColor Yellow
    Write-Host "  1. Check Docker Desktop is running" -ForegroundColor White
    Write-Host "  2. Check container logs: docker-compose -f docker-compose.prod.yml logs" -ForegroundColor White
    Write-Host "  3. Verify ports 3000 and 8000 are not in use" -ForegroundColor White
    Write-Host "  4. Try restarting: docker-compose -f docker-compose.prod.yml restart" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

