# Database Setup Script for Production
# Creates Hebrew database, runs migrations, and seeds data

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Split-Path -Parent $ScriptDir
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $BackendDir)

# Load environment variables
$EnvFile = Join-Path $ProjectRoot ".env.production"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $Name = $matches[1].Trim()
            $Value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($Name, $Value, "Process")
        }
    }
}

$PostgresPassword = $env:POSTGRES_PASSWORD
if ([string]::IsNullOrWhiteSpace($PostgresPassword)) {
    $PostgresPassword = "postgres"
}

Write-Host "Database password: $PostgresPassword" -ForegroundColor Gray
Write-Host ""

# Step 1: Run migrations
Write-Host "Step 1: Running database migrations..." -ForegroundColor Yellow
docker-compose -f (Join-Path $ProjectRoot "docker-compose.prod.yml") exec -T backend alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to run migrations!" -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    
    # Alternative: Run migrations directly
    docker-compose -f (Join-Path $ProjectRoot "docker-compose.prod.yml") exec backend sh -c "cd /app && alembic upgrade head"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Migrations failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ Migrations completed" -ForegroundColor Green
Write-Host ""

# Step 2: Create Hebrew database with sample data
Write-Host "Step 2: Creating Hebrew sample database..." -ForegroundColor Yellow

$CreateDbScript = Join-Path $ScriptDir "create_hebrew_sample_db.py"
if (-not (Test-Path $CreateDbScript)) {
    Write-Host "✗ Hebrew database creation script not found!" -ForegroundColor Red
    Write-Host "Skipping Hebrew database creation..." -ForegroundColor Yellow
} else {
    # The DATABASE_URL should already be set in docker-compose.prod.yml
    # But we'll ensure it's correct for the Hebrew database
    $DatabaseUrl = "postgresql://postgres:$PostgresPassword@database:5432/tama38_hebrew_sample"
    
    # Run the script with explicit DATABASE_URL
    docker-compose -f (Join-Path $ProjectRoot "docker-compose.prod.yml") exec -T backend sh -c "export DATABASE_URL='$DatabaseUrl' && python scripts/create_hebrew_sample_db.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ Hebrew database creation had issues, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✓ Hebrew sample database created" -ForegroundColor Green
    }
}

Write-Host ""

# Step 3: Create admin user
Write-Host "Step 3: Creating admin user..." -ForegroundColor Yellow

$CreateAdminScript = Join-Path $ScriptDir "create_admin.py"
if (-not (Test-Path $CreateAdminScript)) {
    Write-Host "✗ Admin creation script not found!" -ForegroundColor Red
} else {
    docker-compose -f (Join-Path $ProjectRoot "docker-compose.prod.yml") exec -T backend python scripts/create_admin.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ Admin user creation had issues" -ForegroundColor Yellow
        Write-Host "You may need to create admin user manually:" -ForegroundColor Yellow
        Write-Host "  docker-compose -f docker-compose.prod.yml exec backend python scripts/create_admin.py" -ForegroundColor Gray
    } else {
        Write-Host "✓ Admin user created" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Database Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

