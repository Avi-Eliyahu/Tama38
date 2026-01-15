# Quick switch to local Docker environment
# Usage: . .\scripts\docker-local.ps1

$env:DOCKER_COMPOSE_FILE = "docker-compose.yml"
Remove-Item Env:\VITE_API_URL -ErrorAction SilentlyContinue
Remove-Item Env:\CORS_ORIGINS -ErrorAction SilentlyContinue
Set-Content -Path ".docker-env" -Value "local" -Force

Write-Host "✓ Switched to LOCAL Docker environment" -ForegroundColor Green
Write-Host "  Using: docker-compose.yml" -ForegroundColor Gray
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "  Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

