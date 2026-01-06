# TAMA38 Installation Script for Windows

$ErrorActionPreference = "Stop"

Write-Host "TAMA38 Installation Script"
Write-Host ""

# Check Docker
Write-Host "Checking Docker..."
docker --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop is not installed or not running!"
    exit 1
}

docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker daemon is not running!"
    exit 1
}

$InstallDir = $PSScriptRoot

if (-not (Test-Path (Join-Path $InstallDir "docker-compose.prod.yml"))) {
    Write-Host "ERROR: docker-compose.prod.yml not found!"
    exit 1
}

# Environment configuration
Write-Host "Configuring environment..."
$EnvFile = Join-Path $InstallDir ".env.production"
$EnvTemplate = Join-Path $InstallDir "env.production.template"

# Always create env file from template if not exists
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvTemplate $EnvFile -Force
}

# Generate default secure keys
$Bytes = New-Object byte[] 32
$RNG = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
$RNG.GetBytes($Bytes)
$DefaultSecretKey = [Convert]::ToBase64String($Bytes)
$RNG.GetBytes($Bytes)
$DefaultJwtSecretKey = [Convert]::ToBase64String($Bytes)

# Update env file with generated keys if they have placeholder values
$EnvContent = Get-Content $EnvFile -Raw
if ($EnvContent -match "CHANGE-THIS") {
    $EnvContent = $EnvContent -replace "SECRET_KEY=.*", "SECRET_KEY=$DefaultSecretKey"
    $EnvContent = $EnvContent -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$DefaultJwtSecretKey"
    Set-Content $EnvFile -Value $EnvContent
    Write-Host "Generated secure keys"
}

# Build Docker images
Write-Host ""
Write-Host "Building Docker images (this may take several minutes)..."
docker-compose --env-file $EnvFile -f docker-compose.prod.yml build

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build Docker images!"
    exit 1
}

# Start database
Write-Host ""
Write-Host "Starting database..."
docker-compose --env-file $EnvFile -f docker-compose.prod.yml up -d database

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start database!"
    exit 1
}

# Wait for database
Write-Host "Waiting for database to be ready..."
$MaxWait = 60
$Waited = 0
$DatabaseReady = $false

while ($Waited -lt $MaxWait) {
    $HealthCheck = docker-compose --env-file $EnvFile -f docker-compose.prod.yml ps database 2>&1
    if ($HealthCheck -match "healthy") {
        $DatabaseReady = $true
        break
    }
    Start-Sleep -Seconds 2
    $Waited += 2
    Write-Host "."
}

if ($DatabaseReady -eq $false) {
    Write-Host ""
    Write-Host "ERROR: Database did not become ready in time!"
    exit 1
}

Write-Host ""

# Run database setup
Write-Host "Setting up database..."
$SetupScript = Join-Path $InstallDir "backend\scripts\setup_production_database.ps1"
if (Test-Path $SetupScript) {
    & $SetupScript
}

# Start all services
Write-Host ""
Write-Host "Starting all services..."
docker-compose --env-file $EnvFile -f docker-compose.prod.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services!"
    exit 1
}

# Wait for services
Write-Host "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Installation complete
Write-Host ""
Write-Host "Installation Complete!"
Write-Host ""
Write-Host "Access the application:"
Write-Host "  Frontend:  http://localhost:3000"
Write-Host "  Backend:   http://localhost:8000"
Write-Host "  API Docs:  http://localhost:8000/docs"
Write-Host ""
Write-Host "Default Admin Credentials:"
Write-Host "  Email:    admin@tama38.local"
Write-Host "  Password: Admin123!@#"
Write-Host ""
Write-Host "IMPORTANT: Change the admin password after first login!"
Write-Host ""
