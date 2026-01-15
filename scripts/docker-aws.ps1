# Quick switch to AWS Docker environment
# Usage: . .\scripts\docker-aws.ps1 [EC2_IP]
# Example: . .\scripts\docker-aws.ps1 54.123.45.67

param(
    [string]$EC2IP = ""
)

$env:DOCKER_COMPOSE_FILE = "docker-compose.aws.yml"
Set-Content -Path ".docker-env" -Value "aws" -Force

if ($EC2IP) {
    $env:VITE_API_URL = "http://${EC2IP}:8000"
    $env:CORS_ORIGINS = "http://${EC2IP}:3000"
    Write-Host "✓ Switched to AWS Docker environment" -ForegroundColor Yellow
    Write-Host "  Using: docker-compose.aws.yml" -ForegroundColor Gray
    Write-Host "  EC2 IP: $EC2IP" -ForegroundColor Gray
    Write-Host "  VITE_API_URL: $env:VITE_API_URL" -ForegroundColor Gray
    Write-Host "  CORS_ORIGINS: $env:CORS_ORIGINS" -ForegroundColor Gray
} else {
    Write-Host "✓ Switched to AWS Docker environment" -ForegroundColor Yellow
    Write-Host "  Using: docker-compose.aws.yml" -ForegroundColor Gray
    Write-Host "  EC2 IP: Not set" -ForegroundColor Yellow
    Write-Host "  Set VITE_API_URL and CORS_ORIGINS if needed:" -ForegroundColor Gray
    Write-Host "    `$env:VITE_API_URL = 'http://YOUR_EC2_IP:8000'" -ForegroundColor Gray
    Write-Host "    `$env:CORS_ORIGINS = 'http://YOUR_EC2_IP:3000'" -ForegroundColor Gray
}
Write-Host ""

