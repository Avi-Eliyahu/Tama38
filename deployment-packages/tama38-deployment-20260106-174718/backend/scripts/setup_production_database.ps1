# Database Setup Script for Production
# Creates database, runs migrations, and seeds data

$ErrorActionPreference = "Stop"

Write-Host "Database Setup"
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

$ComposeFile = Join-Path $ProjectRoot "docker-compose.prod.yml"

# Step 1: Run migrations
Write-Host "Step 1: Running database migrations..."
docker-compose -f $ComposeFile exec -T backend alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "Migrations failed with exec, trying run..."
    docker-compose -f $ComposeFile run --rm backend alembic upgrade head
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Migrations failed!"
        exit 1
    }
}

Write-Host "Migrations completed"
Write-Host ""

# Step 2: Create Hebrew database with sample data
Write-Host "Step 2: Creating Hebrew sample database..."

$CreateDbScript = Join-Path $ScriptDir "create_hebrew_sample_db.py"
if (-not (Test-Path $CreateDbScript)) {
    Write-Host "Hebrew database creation script not found, skipping..."
} else {
    $DatabaseUrl = "postgresql://postgres:${PostgresPassword}@database:5432/tama38_hebrew_sample"
    
    docker-compose -f $ComposeFile exec -T backend python scripts/create_hebrew_sample_db.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Hebrew database creation had issues, but continuing..."
    } else {
        Write-Host "Hebrew sample database created"
    }
}

Write-Host ""

# Step 3: Create admin user
Write-Host "Step 3: Creating admin user..."

$CreateAdminScript = Join-Path $ScriptDir "create_admin.py"
if (-not (Test-Path $CreateAdminScript)) {
    Write-Host "Admin creation script not found!"
} else {
    docker-compose -f $ComposeFile exec -T backend python scripts/create_admin.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Admin user creation had issues"
        Write-Host "You may need to create admin user manually"
    } else {
        Write-Host "Admin user created"
    }
}

Write-Host ""
Write-Host "Database Setup Complete!"
Write-Host ""
