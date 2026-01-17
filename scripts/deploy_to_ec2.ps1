# Automated EC2 Deployment Script for TAMA38
# Usage: 
#   .\scripts\deploy_to_ec2.ps1                    # Deploy all changes
#   .\scripts\deploy_to_ec2.ps1 -Files "backend/app/api/v1/auth.py"  # Deploy specific files
#   .\scripts\deploy_to_ec2.ps1 -Auto             # Auto-detect changed files from git

param(
    [Parameter(Mandatory=$false)]
    [string[]]$Files = @(),
    
    [Parameter(Mandatory=$false)]
    [switch]$Auto,
    
    [Parameter(Mandatory=$false)]
    [switch]$FullDeploy,
    
    [Parameter(Mandatory=$false)]
    [string]$EC2PublicIP = "",
    
    [Parameter(Mandatory=$false)]
    [string]$EC2User = "ec2-user"
)

$ErrorActionPreference = "Stop"

# Load EC2 configuration if exists
$ec2ConfigPath = ".ec2-config.json"
if (Test-Path $ec2ConfigPath) {
    $ec2Config = Get-Content $ec2ConfigPath | ConvertFrom-Json
    if (-not $EC2PublicIP) {
        $EC2PublicIP = $ec2Config.EC2PublicIP
    }
    if (-not $EC2User) {
        $EC2User = $ec2Config.EC2User
    }
    $SSHKey = $ec2Config.SSHKey
} else {
    # Default values
    if (-not $EC2PublicIP) {
        Write-Host "Error: EC2 Public IP not specified. Either:" -ForegroundColor Red
        Write-Host "  1. Create .ec2-config.json file (see below)" -ForegroundColor Yellow
        Write-Host "  2. Use -EC2PublicIP parameter" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Example .ec2-config.json:" -ForegroundColor Cyan
        Write-Host '{' -ForegroundColor Gray
        Write-Host '  "EC2PublicIP": "63.178.167.164",' -ForegroundColor Gray
        Write-Host '  "EC2User": "ec2-user",' -ForegroundColor Gray
        Write-Host '  "SSHKey": "C:\\Users\\aviel\\.ssh\\tama38-keypair.pem"' -ForegroundColor Gray
        Write-Host '}' -ForegroundColor Gray
        exit 1
    }
    $SSHKey = "$env:USERPROFILE\.ssh\tama38-keypair.pem"
}

# Validate SSH key
if (-not (Test-Path $SSHKey)) {
    Write-Host "Error: SSH key not found at $SSHKey" -ForegroundColor Red
    exit 1
}
$SSHKeyOption = "-i `"$SSHKey`""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Automated EC2 Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "EC2 Public IP: $EC2PublicIP" -ForegroundColor Yellow
Write-Host "EC2 User: $EC2User" -ForegroundColor Yellow
Write-Host "SSH Key: $SSHKey" -ForegroundColor Yellow
Write-Host ""

# Determine files to deploy
$filesToDeploy = @()

if ($FullDeploy) {
    Write-Host "Mode: Full deployment" -ForegroundColor Cyan
    $filesToDeploy = @("backend/", "frontend/", "docker-compose.aws.yml", "scripts/")
} elseif ($Auto) {
    Write-Host "Mode: Auto-detect changed files from git" -ForegroundColor Cyan
    try {
        # Get changed files from last commit
        $changedFiles = git diff --name-only HEAD~1 HEAD 2>$null
        if (-not $changedFiles) {
            # If no previous commit, get all tracked files
            $changedFiles = git ls-files 2>$null
        }
        
        if ($changedFiles) {
            $filesToDeploy = $changedFiles | Where-Object { 
                $_ -match "^backend/" -or 
                $_ -match "^frontend/" -or 
                $_ -eq "docker-compose.aws.yml" -or
                $_ -match "^scripts/"
            }
        }
        
        if ($filesToDeploy.Count -eq 0) {
            Write-Host "No relevant files changed. Exiting." -ForegroundColor Yellow
            exit 0
        }
        
        Write-Host "Found $($filesToDeploy.Count) file(s) to deploy:" -ForegroundColor Green
        $filesToDeploy | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    } catch {
        Write-Host "Warning: Could not detect changed files. Falling back to full deployment." -ForegroundColor Yellow
        $filesToDeploy = @("backend/", "frontend/", "docker-compose.aws.yml", "scripts/")
    }
} elseif ($Files.Count -gt 0) {
    Write-Host "Mode: Deploy specific files" -ForegroundColor Cyan
    $filesToDeploy = $Files
    Write-Host "Files to deploy:" -ForegroundColor Green
    $filesToDeploy | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
} else {
    Write-Host "Mode: Full deployment (no files specified)" -ForegroundColor Cyan
    $filesToDeploy = @("backend/", "frontend/", "docker-compose.aws.yml", "scripts/")
}

Write-Host ""

# Determine which services need restart
$needsBackendRestart = $false
$needsFrontendRestart = $false
$needsFullRestart = $false

foreach ($file in $filesToDeploy) {
    if ($file -match "^backend/" -or $file -match "^scripts/.*\.py$" -or $file -eq "docker-compose.aws.yml") {
        $needsBackendRestart = $true
    }
    if ($file -match "^frontend/" -or $file -eq "docker-compose.aws.yml") {
        $needsFrontendRestart = $true
    }
    if ($file -eq "docker-compose.aws.yml") {
        $needsFullRestart = $true
    }
}

Write-Host "Services to restart:" -ForegroundColor Yellow
if ($needsBackendRestart) { Write-Host "  ✓ Backend" -ForegroundColor Green }
if ($needsFrontendRestart) { Write-Host "  ✓ Frontend" -ForegroundColor Green }
if ($needsFullRestart) { Write-Host "  ✓ Full restart (docker-compose changed)" -ForegroundColor Yellow }
Write-Host ""

# Copy files to EC2
Write-Host "Step 1: Copying files to EC2..." -ForegroundColor Cyan

$scpFiles = $filesToDeploy -join " "
$scpCommand = "scp $SSHKeyOption -r $scpFiles ${EC2User}@${EC2PublicIP}:/home/${EC2User}/tama38/"

try {
    Invoke-Expression $scpCommand
    if ($LASTEXITCODE -ne 0) {
        throw "SCP failed with exit code $LASTEXITCODE"
    }
    Write-Host "✓ Files copied successfully!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Error: Failed to copy files. Check SSH connection and key permissions." -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    exit 1
}

# Deploy on EC2
Write-Host "Step 2: Restarting services on EC2..." -ForegroundColor Cyan

# Build SSH command based on what needs to be restarted
if ($needsFullRestart) {
    $restartCommand = @"
cd ~/tama38

# Get EC2 public IP
EC2_IP=`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "${EC2PublicIP}")

# Export environment variables
export VITE_API_URL="http://`${EC2_IP}:8000"
export CORS_ORIGINS="http://`${EC2_IP}:3000"

echo "Restarting all services..."
docker-compose -f docker-compose.aws.yml restart

# If docker-compose.yml changed, rebuild
echo "Rebuilding containers..."
docker-compose -f docker-compose.aws.yml up -d --build

# Wait for services
sleep 10

# Run migrations if backend changed
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head || echo "Migrations skipped"

echo ""
echo "Container status:"
docker-compose -f docker-compose.aws.yml ps
"@
} elseif ($needsBackendRestart -and $needsFrontendRestart) {
    $restartCommand = @"
cd ~/tama38

echo "Restarting backend and frontend..."
docker-compose -f docker-compose.aws.yml restart backend frontend

# Rebuild if needed
docker-compose -f docker-compose.aws.yml up -d --build backend frontend

sleep 10

# Run migrations
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head || echo "Migrations skipped"

echo ""
echo "Container status:"
docker-compose -f docker-compose.aws.yml ps
"@
} elseif ($needsBackendRestart) {
    $restartCommand = @"
cd ~/tama38

echo "Restarting backend..."
docker-compose -f docker-compose.aws.yml restart backend

# Rebuild backend
docker-compose -f docker-compose.aws.yml up -d --build backend

sleep 10

# Run migrations
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head || echo "Migrations skipped"

echo ""
echo "Container status:"
docker-compose -f docker-compose.aws.yml ps
"@
} elseif ($needsFrontendRestart) {
    $restartCommand = @"
cd ~/tama38

# Get EC2 public IP
EC2_IP=`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "${EC2PublicIP}")

# Export environment variables
export VITE_API_URL="http://`${EC2_IP}:8000"
export CORS_ORIGINS="http://`${EC2_IP}:3000"

echo "Restarting frontend..."
docker-compose -f docker-compose.aws.yml restart frontend

# Rebuild frontend
docker-compose -f docker-compose.aws.yml up -d --build frontend

sleep 5

echo ""
echo "Container status:"
docker-compose -f docker-compose.aws.yml ps
"@
} else {
    Write-Host "No services need restarting. Files copied successfully." -ForegroundColor Green
    exit 0
}

try {
    # Convert Windows line endings (CRLF) to Unix (LF) for Linux compatibility
    $restartCommand = $restartCommand -replace "`r`n", "`n" -replace "`r", "`n"
    
    # Use stdin redirection to avoid quote escaping issues and line ending problems
    # Parse SSH key option properly - it's in format: "-i `"path`""
    $sshArgs = @()
    if ($SSHKeyOption) {
        # Extract the key path from the option string
        if ($SSHKeyOption -match '-i\s+"?([^"]+)"?') {
            $sshArgs = @("-i", $matches[1])
        } elseif ($SSHKeyOption -match '-i\s+(\S+)') {
            $sshArgs = @("-i", $matches[1])
        }
    }
    $sshArgs += "${EC2User}@${EC2PublicIP}"
    $sshArgs += "bash"
    
    # Pipe command to SSH
    $restartCommand | & ssh.exe $sshArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "Deployment completed successfully!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access the application:" -ForegroundColor Yellow
        Write-Host "  Frontend: http://${EC2PublicIP}:3000" -ForegroundColor Cyan
        Write-Host "  Backend API: http://${EC2PublicIP}:8000" -ForegroundColor Cyan
        Write-Host "  API Docs: http://${EC2PublicIP}:8000/docs" -ForegroundColor Cyan
        Write-Host ""
    } else {
        throw "SSH deployment failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host ""
    Write-Host "Error: Deployment failed. Check the output above for details." -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    exit 1
}

