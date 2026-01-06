# TAMA38 Installation Script for Windows
# Automated installation script for production deployment

$ErrorActionPreference = "Stop"

Write-Host "TAMA38 Installation Script"
Write-Host ""

# Check Docker
Write-Host "Checking Docker..."
try {
    docker --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not found"
    }
} catch {
    Write-Host "ERROR: Docker Desktop is not installed or not running!"
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
}

try {
    docker ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon not running"
    }
} catch {
    Write-Host "ERROR: Docker daemon is not running!"
    Write-Host "Please start Docker Desktop and wait for it to fully start."
    exit 1
}

# Get installation directory
$InstallDir = $PSScriptRoot

# Check if docker-compose.prod.yml exists
if (-not (Test-Path (Join-Path $InstallDir "docker-compose.prod.yml"))) {
    Write-Host "ERROR: docker-compose.prod.yml not found!"
    Write-Host "Make sure you're running this script from the extracted package directory."
    exit 1
}

# Environment configuration
Write-Host "Configuring environment..."
$EnvFile = Join-Path $InstallDir ".env.production"
$EnvTemplate = Join-Path $InstallDir "env.production.template"

if (Test-Path $EnvFile) {
    $UseExisting = Read-Host "Use existing configuration? (Y/n)"
    if ($UseExisting -eq "n" -or $UseExisting -eq "N") {
        Copy-Item $EnvTemplate $EnvFile -Force
    }
} else {
    Copy-Item $EnvTemplate $EnvFile -Force
}

$ConfigChoice = Read-Host "Configuration: 1=Defaults, 2=Custom [default: 1]"
if ([string]::IsNullOrWhiteSpace($ConfigChoice)) {
    $ConfigChoice = "1"
}

if ($ConfigChoice -eq "2") {
    $PostgresPassword = Read-Host "Database Password [default: postgres]"
    if ([string]::IsNullOrWhiteSpace($PostgresPassword)) {
        $PostgresPassword = "postgres"
    }
    
    $GenerateKeys = Read-Host "Generate secure secret keys automatically? (Y/n) [default: Y]"
    if ([string]::IsNullOrWhiteSpace($GenerateKeys)) {
        $GenerateKeys = "Y"
    }
    
    if ($GenerateKeys -eq "Y" -or $GenerateKeys -eq "y") {
        $Bytes = New-Object byte[] 32
        $RNG = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
        $RNG.GetBytes($Bytes)
        $SecretKey = [Convert]::ToBase64String($Bytes)
        $RNG.GetBytes($Bytes)
        $JwtSecretKey = [Convert]::ToBase64String($Bytes)
    } else {
        $SecretKey = Read-Host "SECRET_KEY"
        $JwtSecretKey = Read-Host "JWT_SECRET_KEY"
    }
    
    $ApiUrl = Read-Host "API URL [default: http://localhost:8000]"
    if ([string]::IsNullOrWhiteSpace($ApiUrl)) {
        $ApiUrl = "http://localhost:8000"
    }
    
    $EnvContent = Get-Content $EnvFile -Raw
    $EnvContent = $EnvContent -replace "POSTGRES_PASSWORD=.*", "POSTGRES_PASSWORD=$PostgresPassword"
    $EnvContent = $EnvContent -replace "SECRET_KEY=.*", "SECRET_KEY=$SecretKey"
    $EnvContent = $EnvContent -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$JwtSecretKey"
    $EnvContent = $EnvContent -replace "VITE_API_URL=.*", "VITE_API_URL=$ApiUrl"
    Set-Content $EnvFile -Value $EnvContent
}

# Build Docker images
Write-Host ""
Write-Host "Building Docker images (this may take several minutes)..."
docker-compose -f docker-compose.prod.yml build

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build Docker images!"
    exit 1
}

# Start database
Write-Host ""
Write-Host "Starting database..."
docker-compose -f docker-compose.prod.yml up -d database

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
    $HealthCheck = docker-compose -f docker-compose.prod.yml ps database 2>&1
    $HealthStatus = $HealthCheck | Select-String -Pattern "healthy"
    if ($HealthStatus -ne $null) {
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
    Write-Host "Check logs: docker-compose -f docker-compose.prod.yml logs database"
    exit 1
}

Write-Host ""

# Run database setup
Write-Host "Setting up database..."
$SetupScript = Join-Path $InstallDir "backend\scripts\setup_production_database.ps1"
if (Test-Path $SetupScript) {
    & $SetupScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Database setup failed!"
        exit 1
    }
}

# Start all services
Write-Host ""
Write-Host "Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services!"
    exit 1
}

# Wait for services
Write-Host "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Run verification
$VerifyScript = Join-Path $InstallDir "scripts\verify_installation.ps1"
if (Test-Path $VerifyScript) {
    & $VerifyScript
}

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
