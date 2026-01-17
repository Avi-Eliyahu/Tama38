# Docker Environment Toggle Functions
# Usage: Import this file in your PowerShell session: . .\scripts\docker-env.ps1

# Set environment mode (local or aws)
function Set-DockerEnv {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("local", "aws")]
        [string]$Mode
    )
    
    if ($Mode -eq "local") {
        $env:DOCKER_COMPOSE_FILE = "docker-compose.yml"
        Write-Host "✓ Docker environment set to LOCAL" -ForegroundColor Green
        Write-Host "  Using: docker-compose.yml" -ForegroundColor Gray
        Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Gray
        Write-Host "  Backend: http://localhost:8000" -ForegroundColor Gray
        
        # Clear AWS-specific variables
        Remove-Item Env:\VITE_API_URL -ErrorAction SilentlyContinue
        Remove-Item Env:\CORS_ORIGINS -ErrorAction SilentlyContinue
    } else {
        $env:DOCKER_COMPOSE_FILE = "docker-compose.aws.yml"
        Write-Host "✓ Docker environment set to AWS" -ForegroundColor Yellow
        Write-Host "  Using: docker-compose.aws.yml" -ForegroundColor Gray
        
        # Prompt for AWS-specific variables if not set
        if (-not $env:VITE_API_URL) {
            Write-Host ""
            $ip = Read-Host "Enter EC2 Public IP (or press Enter to use default EC2_PUBLIC_IP)"
            if ($ip) {
                $env:VITE_API_URL = "http://${ip}:8000"
                $env:CORS_ORIGINS = "http://${ip}:3000"
                Write-Host "  Set VITE_API_URL=$env:VITE_API_URL" -ForegroundColor Gray
                Write-Host "  Set CORS_ORIGINS=$env:CORS_ORIGINS" -ForegroundColor Gray
            } else {
                Write-Host "  Using default EC2_PUBLIC_IP placeholder" -ForegroundColor Yellow
                Write-Host "  Remember to set VITE_API_URL and CORS_ORIGINS before deployment" -ForegroundColor Yellow
            }
        }
    }
    
    # Save to file for persistence
    Set-Content -Path ".docker-env" -Value $Mode -Force
    Write-Host ""
}

# Get current environment
function Get-DockerEnv {
    if (Test-Path ".docker-env") {
        $mode = (Get-Content ".docker-env" -Raw).Trim()
        $composeFile = if ($mode -eq "local") { "docker-compose.yml" } else { "docker-compose.aws.yml" }
        
        Write-Host "Current Docker environment: $mode" -ForegroundColor Cyan
        Write-Host "Compose file: $composeFile" -ForegroundColor Gray
        
        if ($env:DOCKER_COMPOSE_FILE) {
            Write-Host "Active DOCKER_COMPOSE_FILE: $env:DOCKER_COMPOSE_FILE" -ForegroundColor Gray
        }
        
        if ($env:VITE_API_URL) {
            Write-Host "VITE_API_URL: $env:VITE_API_URL" -ForegroundColor Gray
        }
        if ($env:CORS_ORIGINS) {
            Write-Host "CORS_ORIGINS: $env:CORS_ORIGINS" -ForegroundColor Gray
        }
    } else {
        Write-Host "No Docker environment set. Use Set-DockerEnv local or Set-DockerEnv aws" -ForegroundColor Yellow
    }
}

# Wrapper for docker compose commands
function docker-compose {
    param(
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )
    
    # Load saved environment
    if (Test-Path ".docker-env") {
        $savedMode = (Get-Content ".docker-env" -Raw).Trim()
        if ($savedMode -eq "local") {
            $env:DOCKER_COMPOSE_FILE = "docker-compose.yml"
        } else {
            $env:DOCKER_COMPOSE_FILE = "docker-compose.aws.yml"
        }
    } elseif (-not $env:DOCKER_COMPOSE_FILE) {
        # Default to local if not set
        $env:DOCKER_COMPOSE_FILE = "docker-compose.yml"
        Write-Host "No environment set, defaulting to LOCAL" -ForegroundColor Yellow
    }
    
    # Build docker compose command
    $composeFile = $env:DOCKER_COMPOSE_FILE
    $cmd = "docker", "compose", "-f", $composeFile
    $cmd += $Arguments
    
    Write-Host "[$composeFile] " -ForegroundColor DarkGray -NoNewline
    & $cmd[0] $cmd[1..($cmd.Length-1)]
}

# Convenience functions
function docker-up {
    docker-compose up -d --build
}

function docker-down {
    docker-compose down
}

function docker-logs {
    param(
        [string]$Service = ""
    )
    
    if ($Service) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs -f
    }
}

function docker-ps {
    docker-compose ps
}

function docker-restart {
    param(
        [string]$Service = ""
    )
    
    if ($Service) {
        docker-compose restart $Service
    } else {
        docker-compose restart
    }
}

function docker-stop {
    docker-compose stop
}

function docker-start {
    docker-compose start
}

