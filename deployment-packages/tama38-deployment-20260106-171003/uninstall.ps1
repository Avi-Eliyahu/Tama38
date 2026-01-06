# TAMA38 Uninstallation Script
# Removes TAMA38 containers, images, and optionally volumes

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TAMA38 Uninstallation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get installation directory
$InstallDir = $PSScriptRoot
$ComposeFile = Join-Path $InstallDir "docker-compose.prod.yml"

if (-not (Test-Path $ComposeFile)) {
    Write-Host "✗ docker-compose.prod.yml not found!" -ForegroundColor Red
    Write-Host "Make sure you're running this script from the installation directory." -ForegroundColor Yellow
    exit 1
}

# Warning
Write-Host "WARNING: This will remove all TAMA38 containers and images." -ForegroundColor Yellow
Write-Host ""
$Confirm = Read-Host "Are you sure you want to uninstall TAMA38? (yes/NO)"
if ($Confirm -ne "yes") {
    Write-Host "Uninstallation cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Step 1: Stop containers
Write-Host "Step 1: Stopping containers..." -ForegroundColor Yellow
docker-compose -f $ComposeFile stop

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Containers stopped" -ForegroundColor Green
} else {
    Write-Host "⚠ Some containers may not have stopped" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Remove containers
Write-Host "Step 2: Removing containers..." -ForegroundColor Yellow
docker-compose -f $ComposeFile down

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Containers removed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some containers may not have been removed" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Remove images
Write-Host "Step 3: Removing Docker images..." -ForegroundColor Yellow

$Images = @(
    "tama38_backend_prod",
    "tama38_frontend_prod"
)

foreach ($Image in $Images) {
    $ImageId = docker images --format "{{.ID}}" --filter "reference=*$Image*" 2>&1
    if ($ImageId) {
        docker rmi -f $ImageId 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Removed $Image" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Could not remove $Image" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# Step 4: Remove volumes (optional)
Write-Host "Step 4: Database and storage volumes..." -ForegroundColor Yellow
Write-Host ""
Write-Host "WARNING: Removing volumes will delete all database data and uploaded files!" -ForegroundColor Red
Write-Host "This action cannot be undone." -ForegroundColor Red
Write-Host ""
$RemoveVolumes = Read-Host "Remove volumes? (yes/NO)"
if ($RemoveVolumes -eq "yes") {
    docker-compose -f $ComposeFile down -v
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Volumes removed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Some volumes may not have been removed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Volumes preserved (data is still available)" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Clean up Docker (optional)
Write-Host "Step 5: Docker cleanup..." -ForegroundColor Yellow
$CleanDocker = Read-Host "Remove unused Docker resources? (y/N)"
if ($CleanDocker -eq "y" -or $CleanDocker -eq "Y") {
    docker system prune -f
    Write-Host "✓ Docker cleanup completed" -ForegroundColor Green
} else {
    Write-Host "Skipped Docker cleanup" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Remove installation directory (optional)
Write-Host "Step 6: Installation directory..." -ForegroundColor Yellow
Write-Host "Installation directory: $InstallDir" -ForegroundColor Gray
$RemoveDir = Read-Host "Remove installation directory? (yes/NO)"
if ($RemoveDir -eq "yes") {
    Write-Host "Removing installation directory..." -ForegroundColor Yellow
    Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $InstallDir) {
        Write-Host "⚠ Could not completely remove installation directory" -ForegroundColor Yellow
        Write-Host "You may need to remove it manually: $InstallDir" -ForegroundColor Gray
    } else {
        Write-Host "✓ Installation directory removed" -ForegroundColor Green
    }
} else {
    Write-Host "Installation directory preserved" -ForegroundColor Yellow
    Write-Host "You can remove it manually later if needed." -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Uninstallation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($RemoveVolumes -ne "yes") {
    Write-Host "Note: Database volumes were preserved." -ForegroundColor Yellow
    Write-Host "To remove them later, run:" -ForegroundColor Gray
    Write-Host "  docker volume ls" -ForegroundColor Gray
    Write-Host "  docker volume rm <volume_name>" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "TAMA38 has been uninstalled." -ForegroundColor Cyan
Write-Host ""

