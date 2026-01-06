# TAMA38 Deployment Package Creator
# Creates a self-contained deployment package for Windows installation

param(
    [string]$OutputDir = ".\deployment-packages"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TAMA38 Deployment Package Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$PackageName = "tama38-deployment-$Timestamp"
$PackageDir = Join-Path $OutputDir $PackageName
$ZipFile = "$PackageName.zip"

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host "Package Directory: $PackageDir" -ForegroundColor Gray
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Create package directory structure
Write-Host "Creating package directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "backend") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "frontend") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "scripts") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "docs") -Force | Out-Null

# Define exclusion patterns
$ExcludePatterns = @(
    ".cursor",
    ".git",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".next",
    "dist",
    "build",
    "*.log",
    "logs",
    ".env",
    ".env.local",
    ".env.*.local",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    "*.zip",
    "*.tar.gz",
    "deployment-packages",
    ".vscode",
    ".idea",
    "backups",
    "*.backup",
    "*.sql",
    "*.pdf",
    "*.docx",
    "*.xlsx",
    "samples"
)

# Function to should exclude file/directory
function Should-Exclude {
    param([string]$Path)
    
    $RelativePath = $Path.Replace($ProjectRoot, "").TrimStart("\")
    
    foreach ($Pattern in $ExcludePatterns) {
        if ($RelativePath -like "*\$Pattern" -or $RelativePath -like "$Pattern\*" -or $RelativePath -eq $Pattern) {
            return $true
        }
    }
    
    return $false
}

# Copy backend files
Write-Host "Copying backend files..." -ForegroundColor Yellow
$BackendSource = Join-Path $ProjectRoot "backend"
$BackendDest = Join-Path $PackageDir "backend"

Get-ChildItem -Path $BackendSource -Recurse -File | ForEach-Object {
    if (-not (Should-Exclude $_.FullName)) {
        $RelativePath = $_.FullName.Replace($BackendSource, "").TrimStart("\")
        $DestPath = Join-Path $BackendDest $RelativePath
        $DestDir = Split-Path -Parent $DestPath
        
        if (-not (Test-Path $DestDir)) {
            New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
        }
        
        Copy-Item -Path $_.FullName -Destination $DestPath -Force
    }
}

# Copy frontend files
Write-Host "Copying frontend files..." -ForegroundColor Yellow
$FrontendSource = Join-Path $ProjectRoot "frontend"
$FrontendDest = Join-Path $PackageDir "frontend"

Get-ChildItem -Path $FrontendSource -Recurse -File | ForEach-Object {
    if (-not (Should-Exclude $_.FullName)) {
        $RelativePath = $_.FullName.Replace($FrontendSource, "").TrimStart("\")
        $DestPath = Join-Path $FrontendDest $RelativePath
        $DestDir = Split-Path -Parent $DestPath
        
        if (-not (Test-Path $DestDir)) {
            New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
        }
        
        Copy-Item -Path $_.FullName -Destination $DestPath -Force
    }
}

# Copy Docker files
Write-Host "Copying Docker configuration files..." -ForegroundColor Yellow
Copy-Item -Path (Join-Path $ProjectRoot "docker-compose.yml") -Destination (Join-Path $PackageDir "docker-compose.yml") -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $ProjectRoot "docker-compose.prod.yml") -Destination (Join-Path $PackageDir "docker-compose.prod.yml") -Force -ErrorAction SilentlyContinue

# Copy production Dockerfiles
if (Test-Path (Join-Path $ProjectRoot "backend\Dockerfile.prod")) {
    Copy-Item -Path (Join-Path $ProjectRoot "backend\Dockerfile.prod") -Destination (Join-Path $PackageDir "backend\Dockerfile.prod") -Force
}
if (Test-Path (Join-Path $ProjectRoot "frontend\Dockerfile.prod")) {
    Copy-Item -Path (Join-Path $ProjectRoot "frontend\Dockerfile.prod") -Destination (Join-Path $PackageDir "frontend\Dockerfile.prod") -Force
}
if (Test-Path (Join-Path $ProjectRoot "frontend\nginx.conf")) {
    Copy-Item -Path (Join-Path $ProjectRoot "frontend\nginx.conf") -Destination (Join-Path $PackageDir "frontend\nginx.conf") -Force
}

# Copy installation scripts
Write-Host "Copying installation scripts..." -ForegroundColor Yellow
Copy-Item -Path (Join-Path $ProjectRoot "install.ps1") -Destination (Join-Path $PackageDir "install.ps1") -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $ProjectRoot "uninstall.ps1") -Destination (Join-Path $PackageDir "uninstall.ps1") -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $ProjectRoot "env.production.template") -Destination (Join-Path $PackageDir "env.production.template") -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $ProjectRoot "INSTALLATION_GUIDE.md") -Destination (Join-Path $PackageDir "INSTALLATION_GUIDE.md") -Force -ErrorAction SilentlyContinue

# Copy database setup scripts
Write-Host "Copying database setup scripts..." -ForegroundColor Yellow
$ScriptsSource = Join-Path $ProjectRoot "backend\scripts"
$ScriptsDest = Join-Path $PackageDir "backend\scripts"

if (Test-Path $ScriptsSource) {
    # Create scripts directory if it doesn't exist
    if (-not (Test-Path $ScriptsDest)) {
        New-Item -ItemType Directory -Path $ScriptsDest -Force | Out-Null
    }
    
    Get-ChildItem -Path $ScriptsSource -Filter "*.py" | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination (Join-Path $ScriptsDest $_.Name) -Force
    }
    Copy-Item -Path (Join-Path $ScriptsSource "setup_production_database.ps1") -Destination (Join-Path $ScriptsDest "setup_production_database.ps1") -Force -ErrorAction SilentlyContinue
}

# Copy verification script
if (Test-Path (Join-Path $ProjectRoot "scripts\verify_installation.ps1")) {
    Copy-Item -Path (Join-Path $ProjectRoot "scripts\verify_installation.ps1") -Destination (Join-Path $PackageDir "scripts\verify_installation.ps1") -Force
}

# Copy README and documentation
Write-Host "Copying documentation..." -ForegroundColor Yellow
if (Test-Path (Join-Path $ProjectRoot "README.md")) {
    Copy-Item -Path (Join-Path $ProjectRoot "README.md") -Destination (Join-Path $PackageDir "README.md") -Force
}
if (Test-Path (Join-Path $ProjectRoot "DEPLOYMENT_README.md")) {
    Copy-Item -Path (Join-Path $ProjectRoot "DEPLOYMENT_README.md") -Destination (Join-Path $PackageDir "DEPLOYMENT_README.md") -Force
}

# Create package README
$PackageReadme = @"
# TAMA38 Deployment Package

This package contains everything needed to install TAMA38 on a Windows machine.

## Contents

- **backend/**: Backend application code
- **frontend/**: Frontend application code
- **docker-compose.prod.yml**: Production Docker Compose configuration
- **install.ps1**: Automated installation script
- **uninstall.ps1**: Uninstallation script
- **INSTALLATION_GUIDE.md**: Detailed installation instructions
- **env.production.template**: Environment variables template

## Quick Start

1. Extract this package to your desired installation directory
2. Open PowerShell as Administrator
3. Run: `.\install.ps1`
4. Follow the on-screen instructions

For detailed instructions, see INSTALLATION_GUIDE.md

## Prerequisites

- Docker Desktop for Windows
- PowerShell 5.1 or later
- Internet connection (for Docker image downloads)

Package created: $Timestamp
"@

Set-Content -Path (Join-Path $PackageDir "README.md") -Value $PackageReadme

# Create ZIP archive
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$ZipPath = Join-Path $OutputDir $ZipFile

# Remove existing ZIP if it exists
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

# Create ZIP using .NET compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($PackageDir, $ZipPath)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Package created successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package Location: $ZipPath" -ForegroundColor Cyan
Write-Host "Package Size: $([math]::Round((Get-Item $ZipPath).Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Transfer $ZipFile to the target Windows machine" -ForegroundColor White
Write-Host "2. Extract the ZIP file" -ForegroundColor White
Write-Host "3. Run install.ps1 on the target machine" -ForegroundColor White
Write-Host ""

