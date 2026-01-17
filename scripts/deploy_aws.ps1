# AWS Deployment Script for TAMA38 (PowerShell)
# Usage: .\scripts\deploy_aws.ps1 -EC2PublicIP <IP> [-EC2User ec2-user|ubuntu]

param(
    [Parameter(Mandatory=$true)]
    [string]$EC2PublicIP,
    
    [Parameter(Mandatory=$false)]
    [string]$EC2User = "ec2-user"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deploying TAMA38 to EC2" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "EC2 Public IP: $EC2PublicIP"
Write-Host "EC2 User: $EC2User"
Write-Host ""

# Set environment variables
$env:VITE_API_URL = "http://${EC2PublicIP}:8000"
$env:CORS_ORIGINS = "http://${EC2PublicIP}:3000"

Write-Host "Environment variables:" -ForegroundColor Yellow
Write-Host "  VITE_API_URL=$env:VITE_API_URL"
Write-Host "  CORS_ORIGINS=$env:CORS_ORIGINS"
Write-Host ""

# Check if SSH key exists
$SSHKey = "$env:USERPROFILE\.ssh\tama38-keypair.pem"
if (-not (Test-Path $SSHKey)) {
    Write-Host "Warning: SSH key not found at $SSHKey" -ForegroundColor Yellow
    Write-Host "Please ensure your SSH key is accessible"
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
    $SSHKeyOption = ""
} else {
    $SSHKeyOption = "-i `"$SSHKey`""
}

# Copy files to EC2
Write-Host "Step 1: Copying files to EC2..." -ForegroundColor Cyan
$scpCommand = "scp $SSHKeyOption -r docker-compose.aws.yml backend/ frontend/ scripts/ ${EC2User}@${EC2PublicIP}:/home/${EC2User}/tama38/"

try {
    Invoke-Expression $scpCommand
    if ($LASTEXITCODE -ne 0) {
        throw "SCP failed with exit code $LASTEXITCODE"
    }
    Write-Host "Files copied successfully!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "Error: Failed to copy files. Check SSH connection and key permissions." -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    exit 1
}

# Deploy on EC2
Write-Host "Step 2: Deploying on EC2..." -ForegroundColor Cyan

$sshCommand = @"
cd ~/tama38

# Get EC2 public IP (in case Elastic IP is used)
EC2_IP=`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "${EC2PublicIP}")

# Export environment variables
export VITE_API_URL="http://`${EC2_IP}:8000"
export CORS_ORIGINS="http://`${EC2_IP}:3000"

echo "Deploying with:"
echo "  VITE_API_URL=`$VITE_API_URL"
echo "  CORS_ORIGINS=`$CORS_ORIGINS"
echo ""

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.aws.yml down || true

# Build and start containers
echo "Building and starting containers..."
docker-compose -f docker-compose.aws.yml up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 15

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head || echo "Warning: Migrations may have failed, check logs"

# Show status
echo ""
echo "Container status:"
docker-compose -f docker-compose.aws.yml ps

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
"@

try {
    $fullSSHCommand = "ssh $SSHKeyOption ${EC2User}@${EC2PublicIP} `"$sshCommand`""
    Invoke-Expression $fullSSHCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "Deployment finished successfully!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Access the application:" -ForegroundColor Yellow
        Write-Host "  Frontend: http://${EC2PublicIP}:3000"
        Write-Host "  Backend API: http://${EC2PublicIP}:8000"
        Write-Host "  API Docs: http://${EC2PublicIP}:8000/docs"
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "  1. Create admin user:"
        Write-Host "     ssh $SSHKeyOption ${EC2User}@${EC2PublicIP}"
        Write-Host "     cd ~/tama38"
        Write-Host "     docker-compose -f docker-compose.aws.yml exec backend python scripts/create_admin.py"
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

