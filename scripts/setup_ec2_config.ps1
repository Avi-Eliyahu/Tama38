# Setup EC2 Configuration File
# Usage: .\scripts\setup_ec2_config.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$EC2PublicIP = "",
    
    [Parameter(Mandatory=$false)]
    [string]$EC2User = "ec2-user",
    
    [Parameter(Mandatory=$false)]
    [string]$SSHKey = ""
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "EC2 Configuration Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if config already exists
$configPath = ".ec2-config.json"
if (Test-Path $configPath) {
    Write-Host "Warning: .ec2-config.json already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/n)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Get EC2 Public IP
if (-not $EC2PublicIP) {
    $EC2PublicIP = Read-Host "Enter EC2 Public IP (e.g., 63.178.167.164)"
}

if (-not $EC2PublicIP) {
    Write-Host "Error: EC2 Public IP is required" -ForegroundColor Red
    exit 1
}

# Get EC2 User
if (-not $EC2User) {
    $EC2User = Read-Host "Enter EC2 User (default: ec2-user)"
    if (-not $EC2User) {
        $EC2User = "ec2-user"
    }
}

# Get SSH Key path
if (-not $SSHKey) {
    $defaultSSHKey = "$env:USERPROFILE\.ssh\tama38-keypair.pem"
    Write-Host "Default SSH key location: $defaultSSHKey" -ForegroundColor Gray
    $SSHKey = Read-Host "Enter SSH key path (or press Enter for default)"
    if (-not $SSHKey) {
        $SSHKey = $defaultSSHKey
    }
}

# Validate SSH key exists
if (-not (Test-Path $SSHKey)) {
    Write-Host "Warning: SSH key not found at $SSHKey" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Create config object
$config = @{
    EC2PublicIP = $EC2PublicIP
    EC2User = $EC2User
    SSHKey = $SSHKey
    AutoDeploy = $true
} | ConvertTo-Json -Depth 10

# Write config file
$config | Set-Content -Path $configPath -Encoding UTF8

Write-Host ""
Write-Host "✓ EC2 configuration saved to .ec2-config.json" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  EC2 Public IP: $EC2PublicIP" -ForegroundColor Gray
Write-Host "  EC2 User: $EC2User" -ForegroundColor Gray
Write-Host "  SSH Key: $SSHKey" -ForegroundColor Gray
Write-Host "  Auto-Deploy: Enabled" -ForegroundColor Gray
Write-Host ""
Write-Host "Note: .ec2-config.json is in .gitignore and will not be committed." -ForegroundColor Yellow
Write-Host ""

