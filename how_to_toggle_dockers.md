# How to Toggle Between Local and AWS Docker Environments

This guide explains how to easily switch between local Docker development and AWS Docker deployment for the TAMA38 system.

---

## Quick Start

### Method 1: Using Functions (Recommended)

**1. Load the Docker Environment Functions**

Open PowerShell in the project root directory and run:

```powershell
. .\scripts\docker-env.ps1
```

**2. Switch Environments**

**Switch to Local (Development):**
```powershell
Set-DockerEnv local
```

**Switch to AWS (Production):**
```powershell
Set-DockerEnv aws
```

**3. Use Docker Commands Normally**

After setting the environment, use docker commands as usual:

```powershell
docker-compose up -d
docker-compose ps
docker-compose logs
```

The functions automatically use the correct compose file (`docker-compose.yml` for local, `docker-compose.aws.yml` for AWS).

### Method 2: Using Simple Scripts (Alternative)

If you prefer simpler scripts without functions:

**Switch to Local:**
```powershell
. .\scripts\docker-local.ps1
docker compose up -d
```

**Switch to AWS:**
```powershell
. .\scripts\docker-aws.ps1 54.123.45.67  # Replace with your EC2 IP
docker compose up -d
```

**Note:** With Method 2, you need to use `docker compose -f $env:DOCKER_COMPOSE_FILE` or the scripts set the environment variable automatically.

---

## Detailed Usage Guide

### Setting Up the Environment

#### First Time Setup

1. **Load the functions** (required each PowerShell session):
   ```powershell
   . .\scripts\docker-env.ps1
   ```

2. **Optional: Add to PowerShell Profile** (so functions load automatically):
   ```powershell
   # Check if profile exists
   Test-Path $PROFILE
   
   # If false, create it
   if (-not (Test-Path $PROFILE)) {
       New-Item -Path $PROFILE -Type File -Force
   }
   
   # Add the import line
   Add-Content -Path $PROFILE -Value ". C:\projects\pinoy\scripts\docker-env.ps1"
   ```

### Switching Between Environments

#### Switch to Local Development

```powershell
Set-DockerEnv local
```

**What this does:**
- Sets `DOCKER_COMPOSE_FILE` to `docker-compose.yml`
- Clears AWS-specific environment variables
- Saves preference to `.docker-env` file
- Uses development settings (hot reload, debug mode)

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Switch to AWS Deployment

```powershell
Set-DockerEnv aws
```

**What this does:**
- Sets `DOCKER_COMPOSE_FILE` to `docker-compose.aws.yml`
- Prompts for EC2 Public IP (if not already set)
- Sets `VITE_API_URL` and `CORS_ORIGINS` environment variables
- Saves preference to `.docker-env` file
- Uses production settings (no hot reload, optimized)

**When prompted for EC2 IP:**
- Enter your EC2 instance public IP (e.g., `54.123.45.67`)
- Or press Enter to skip (you'll need to set it manually later)

**Access URLs (after deployment):**
- Frontend: http://YOUR_EC2_IP:3000
- Backend API: http://YOUR_EC2_IP:8000
- API Docs: http://YOUR_EC2_IP:8000/docs

### Checking Current Environment

```powershell
Get-DockerEnv
```

**Output example:**
```
Current Docker environment: local
Compose file: docker-compose.yml
Active DOCKER_COMPOSE_FILE: docker-compose.yml
```

---

## Common Docker Commands

### Using the Wrapper Functions

After loading `docker-env.ps1`, you can use these convenience functions:

```powershell
# Start all services
docker-up

# Stop all services
docker-down

# View logs (all services)
docker-logs

# View logs for specific service
docker-logs backend
docker-logs frontend
docker-logs database

# Check container status
docker-ps

# Restart all services
docker-restart

# Restart specific service
docker-restart backend

# Stop services (keeps containers)
docker-stop

# Start stopped services
docker-start
```

### Using Standard Docker Compose Commands

The wrapper functions automatically use the correct compose file:

```powershell
# Build and start
docker-compose up -d --build

# Stop and remove containers
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Execute command in container
docker-compose exec backend python scripts/create_admin.py

# Run database migrations
docker-compose exec backend alembic upgrade head
```

---

## Workflow Examples

### Example 1: Working Locally, Then Deploying to AWS

```powershell
# 1. Load functions
. .\scripts\docker-env.ps1

# 2. Work locally
Set-DockerEnv local
docker-up
docker-logs

# 3. When ready to deploy to AWS
Set-DockerEnv aws
# Enter EC2 IP when prompted: 54.123.45.67

# 4. Deploy to AWS (using deployment script)
.\scripts\deploy_aws.ps1 -EC2PublicIP "54.123.45.67"

# 5. Or run locally but with AWS config (for testing)
docker-up
```

### Example 2: Switching Back and Forth

```powershell
# Load functions once
. .\scripts\docker-env.ps1

# Work locally
Set-DockerEnv local
docker-up
# ... do local development ...

# Switch to AWS
Set-DockerEnv aws
docker-down  # Stop local
# ... deploy to AWS or test AWS config ...

# Switch back to local
Set-DockerEnv local
docker-up
# ... continue local development ...
```

### Example 3: Checking What's Running

```powershell
# Check current environment
Get-DockerEnv

# Check container status
docker-ps

# View logs
docker-logs backend
```

---

## Environment Files

### `.docker-env` File

This file stores your current environment preference:
- Created automatically when you run `Set-DockerEnv`
- Contains either `local` or `aws`
- Persists across PowerShell sessions
- Can be safely committed to git (or added to `.gitignore` if you prefer)

### Environment Variables

**Local Environment:**
- `DOCKER_COMPOSE_FILE=docker-compose.yml`
- No AWS-specific variables needed

**AWS Environment:**
- `DOCKER_COMPOSE_FILE=docker-compose.aws.yml`
- `VITE_API_URL=http://YOUR_EC2_IP:8000` (optional, set when prompted)
- `CORS_ORIGINS=http://YOUR_EC2_IP:3000` (optional, set when prompted)

---

## Troubleshooting

### Functions Not Found

**Problem:** `Set-DockerEnv : The term 'Set-DockerEnv' is not recognized`

**Solution:** Load the functions first:
```powershell
. .\scripts\docker-env.ps1
```

### Wrong Compose File Being Used

**Problem:** Docker commands use the wrong compose file

**Solution:** 
1. Check current environment: `Get-DockerEnv`
2. Switch to correct environment: `Set-DockerEnv local` or `Set-DockerEnv aws`
3. Verify: `Get-DockerEnv`

### Environment Variables Not Set for AWS

**Problem:** AWS deployment fails because `VITE_API_URL` is not set

**Solution:**
```powershell
# Set manually
$env:VITE_API_URL = "http://YOUR_EC2_IP:8000"
$env:CORS_ORIGINS = "http://YOUR_EC2_IP:3000"

# Or switch environment again and enter IP when prompted
Set-DockerEnv aws
```

### Containers Using Wrong Configuration

**Problem:** Containers started with wrong settings

**Solution:**
```powershell
# Stop everything
docker-down

# Switch environment
Set-DockerEnv local  # or aws

# Start again
docker-up
```

### PowerShell Execution Policy Error

**Problem:** `cannot be loaded because running scripts is disabled on this system`

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Differences Between Local and AWS Configurations

### Local (`docker-compose.yml`)
- **Environment:** `development`
- **Debug:** `true`
- **Hot Reload:** Enabled (code changes auto-reload)
- **Volumes:** Code mounted for live editing
- **Log Level:** `DEBUG`
- **CORS:** `http://localhost:3000`
- **API URL:** `http://localhost:8000`
- **Restart Policy:** None (manual restart)

### AWS (`docker-compose.aws.yml`)
- **Environment:** `production`
- **Debug:** `false`
- **Hot Reload:** Disabled
- **Volumes:** Only logs and storage (no code mount)
- **Log Level:** `INFO`
- **CORS:** `http://EC2_PUBLIC_IP:3000` (set via env var)
- **API URL:** `http://EC2_PUBLIC_IP:8000` (set via env var)
- **Restart Policy:** `unless-stopped` (auto-restart on failure)

---

## Best Practices

1. **Always check environment before starting:**
   ```powershell
   Get-DockerEnv
   ```

2. **Stop services before switching:**
   ```powershell
   docker-down
   Set-DockerEnv aws
   docker-up
   ```

3. **Use convenience functions:**
   - `docker-up` instead of `docker-compose up -d --build`
   - `docker-logs` instead of `docker-compose logs -f`
   - `docker-ps` instead of `docker-compose ps`

4. **Keep AWS IP handy:**
   - Save your EC2 IP in a note
   - Or set it once and it persists in the session

5. **Verify after switching:**
   ```powershell
   Set-DockerEnv aws
   Get-DockerEnv  # Verify it's correct
   docker-ps      # Check what's running
   ```

---

## Quick Reference

| Command | Description |
|--------|-------------|
| `. .\scripts\docker-env.ps1` | Load Docker environment functions |
| `Set-DockerEnv local` | Switch to local development |
| `Set-DockerEnv aws` | Switch to AWS deployment |
| `Get-DockerEnv` | Show current environment |
| `docker-up` | Start all services |
| `docker-down` | Stop and remove all services |
| `docker-logs` | View all logs |
| `docker-logs backend` | View backend logs |
| `docker-ps` | Show container status |
| `docker-restart` | Restart all services |
| `docker-compose exec backend <cmd>` | Run command in backend container |

---

## Additional Resources

- **AWS Deployment Guide:** See `basic_migration_aws.md`
- **Docker Compose Docs:** https://docs.docker.com/compose/
- **Project README:** See `README.md`

---

**Last Updated:** 2026-01-13  
**Version:** 1.0

