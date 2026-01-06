# TAMA38 Installation Script for Windows
# Automated installation script for production deployment

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TAMA38 Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Host "WARNING: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "Consider running PowerShell as Administrator for best results." -ForegroundColor Yellow
    Write-Host ""
    $Continue = Read-Host "Continue anyway? (y/N)"
    if ($Continue -ne "y" -and $Continue -ne "Y") {
        exit 1
    }
}

# Check Docker Desktop
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    $DockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not found"
    }
    Write-Host "✓ Docker found: $DockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not installed or not running!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "Make sure Docker Desktop is running before proceeding." -ForegroundColor Yellow
    exit 1
}

# Check Docker daemon is running
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon not running"
    }
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and wait for it to fully start." -ForegroundColor Yellow
    exit 1
}

# Get installation directory
$InstallDir = $PSScriptRoot
Write-Host "Installation directory: $InstallDir" -ForegroundColor Gray
Write-Host ""

# Check if docker-compose.prod.yml exists
if (-not (Test-Path (Join-Path $InstallDir "docker-compose.prod.yml"))) {
    Write-Host "✗ docker-compose.prod.yml not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the extracted package directory." -ForegroundColor Yellow
    exit 1
}

# Environment configuration
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Environment Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$EnvFile = Join-Path $InstallDir ".env.production"
$EnvTemplate = Join-Path $InstallDir "env.production.template"

# Load or create environment file
if (Test-Path $EnvFile) {
    Write-Host "Found existing .env.production file" -ForegroundColor Yellow
    $UseExisting = Read-Host "Use existing configuration? (Y/n)"
    if ($UseExisting -eq "n" -or $UseExisting -eq "N") {
        Copy-Item $EnvTemplate $EnvFile -Force
    }
} else {
    Copy-Item $EnvTemplate $EnvFile -Force
    Write-Host "Created .env.production from template" -ForegroundColor Green
}

# Prompt for configuration
Write-Host ""
Write-Host "Configuration Options:" -ForegroundColor Yellow
Write-Host "1. Use defaults (recommended for first-time installation)" -ForegroundColor White
Write-Host "2. Custom configuration" -ForegroundColor White
$ConfigChoice = Read-Host "Choose option (1/2) [default: 1]"

if ([string]::IsNullOrWhiteSpace($ConfigChoice)) {
    $ConfigChoice = "1"
}

if ($ConfigChoice -eq "2") {
    Write-Host ""
    Write-Host "Enter configuration values (press Enter to use defaults):" -ForegroundColor Yellow
    
    $PostgresPassword = Read-Host "Database Password [default: postgres]"
    if ([string]::IsNullOrWhiteSpace($PostgresPassword)) {
        $PostgresPassword = "postgres"
    }
    
    $GenerateKeys = Read-Host "Generate secure secret keys automatically? (Y/n) [default: Y]"
    if ([string]::IsNullOrWhiteSpace($GenerateKeys) -or $GenerateKeys -eq "Y" -or $GenerateKeys -eq "y") {
        # Generate secure keys
        $SecretKey = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
        $JwtSecretKey = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
        Write-Host "✓ Generated secure keys" -ForegroundColor Green
    } else {
        $SecretKey = Read-Host "SECRET_KEY"
        $JwtSecretKey = Read-Host "JWT_SECRET_KEY"
    }
    
    $ApiUrl = Read-Host "API URL [default: http://localhost:8000]"
    if ([string]::IsNullOrWhiteSpace($ApiUrl)) {
        $ApiUrl = "http://localhost:8000"
    }
    
    # Update .env.production
    $EnvContent = Get-Content $EnvFile -Raw
    $EnvContent = $EnvContent -replace "POSTGRES_PASSWORD=.*", "POSTGRES_PASSWORD=$PostgresPassword"
    $EnvContent = $EnvContent -replace "SECRET_KEY=.*", "SECRET_KEY=$SecretKey"
    $EnvContent = $EnvContent -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$JwtSecretKey"
    $EnvContent = $EnvContent -replace "VITE_API_URL=.*", "VITE_API_URL=$ApiUrl"
    Set-Content $EnvFile -Value $EnvContent
} else {
    Write-Host "Using default configuration" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Docker Images" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This may take several minutes on first run..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml build

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to build Docker images!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker images built successfully" -ForegroundColor Green
Write-Host ""

# Start database first
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Database" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

docker-compose -f docker-compose.prod.yml up -d database

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start database!" -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
$MaxWait = 60
$Waited = 0
while ($Waited -lt $MaxWait) {
    $Health = docker-compose -f docker-compose.prod.yml ps database | Select-String "healthy"
    if ($Health) {
        Write-Host "✓ Database is ready" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $Waited += 2
    Write-Host "." -NoNewline -ForegroundColor Gray
}

if ($Waited -ge $MaxWait) {
    Write-Host ""
    Write-Host "✗ Database did not become ready in time!" -ForegroundColor Red
    Write-Host "Check logs: docker-compose -f docker-compose.prod.yml logs database" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Run database setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting Up Database" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SetupScript = Join-Path $InstallDir "backend\scripts\setup_production_database.ps1"
if (Test-Path $SetupScript) {
    & $SetupScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Database setup failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ Database setup script not found, skipping..." -ForegroundColor Yellow
    Write-Host "You may need to run migrations manually:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head" -ForegroundColor Gray
}

Write-Host ""

# Start all services
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting All Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

docker-compose -f docker-compose.prod.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start services!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ All services started" -ForegroundColor Green
Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run verification
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verifying Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$VerifyScript = Join-Path $InstallDir "scripts\verify_installation.ps1"
if (Test-Path $VerifyScript) {
    & $VerifyScript
} else {
    Write-Host "⚠ Verification script not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Default Admin Credentials:" -ForegroundColor Cyan
Write-Host "  Email:    admin@tama38.local" -ForegroundColor White
Write-Host "  Password: Admin123!@#" -ForegroundColor White
Write-Host ""
Write-Host "⚠ IMPORTANT: Change the admin password after first login!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:    docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
Write-Host "  Stop:         docker-compose -f docker-compose.prod.yml stop" -ForegroundColor Gray
Write-Host "  Start:        docker-compose -f docker-compose.prod.yml start" -ForegroundColor Gray
Write-Host "  Restart:      docker-compose -f docker-compose.prod.yml restart" -ForegroundColor Gray
Write-Host "  Uninstall:    .\uninstall.ps1" -ForegroundColor Gray
Write-Host ""

