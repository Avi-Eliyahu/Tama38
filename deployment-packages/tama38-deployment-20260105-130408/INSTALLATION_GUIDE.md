# TAMA38 Installation Guide for Windows

This guide will help you install TAMA38 on a Windows machine using Docker.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop
   - Version: 4.0 or later
   - Make sure Docker Desktop is running before proceeding

2. **PowerShell**
   - Windows 10/11 comes with PowerShell 5.1+ by default
   - Verify by running: `powershell -Command $PSVersionTable.PSVersion`

3. **Internet Connection**
   - Required for downloading Docker images (~500MB)

### System Requirements

- **OS**: Windows 10 (64-bit) or Windows 11
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: At least 10GB free space
- **CPU**: 2+ cores recommended

## Installation Steps

### Step 1: Extract the Package

1. Extract the `tama38-deployment-*.zip` file to your desired installation directory
   - Example: `C:\TAMA38\`
   - Avoid paths with spaces or special characters

2. Open PowerShell as Administrator:
   - Right-click on PowerShell
   - Select "Run as Administrator"

3. Navigate to the extracted directory:
   ```powershell
   cd C:\TAMA38\tama38-deployment-*
   ```

### Step 2: Run the Installation Script

1. **Check execution policy** (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Run the installation script**:
   ```powershell
   .\install.ps1
   ```

3. The script will:
   - Check Docker Desktop is running
   - Prompt for environment configuration
   - Build Docker images
   - Set up the database
   - Create initial admin user
   - Start all services

### Step 3: Configure Environment Variables

During installation, you'll be prompted to configure:

1. **Database Password** (default: `postgres`)
   - Use a strong password in production

2. **Secret Keys**
   - The script can generate secure keys automatically
   - Or you can provide your own

3. **API URL**
   - Default: `http://localhost:8000`
   - Change if deploying to a different domain

### Step 4: Verify Installation

After installation completes, verify everything is working:

1. **Check containers are running**:
   ```powershell
   docker ps
   ```
   You should see three containers: `tama38_database_prod`, `tama38_backend_prod`, `tama38_frontend_prod`

2. **Run verification script**:
   ```powershell
   .\scripts\verify_installation.ps1
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs
   - Backend Health: http://localhost:8000/health

### Step 5: Login

Use the default admin credentials:
- **Email**: `admin@tama38.local`
- **Password**: `Admin123!@#`

**Important**: Change the admin password immediately after first login!

## Manual Installation (Alternative)

If you prefer to install manually:

### 1. Configure Environment

```powershell
Copy-Item env.production.template .env.production
# Edit .env.production with your preferred editor
notepad .env.production
```

### 2. Build Docker Images

```powershell
docker-compose -f docker-compose.prod.yml build
```

### 3. Start Database

```powershell
docker-compose -f docker-compose.prod.yml up -d database
```

### 4. Wait for Database

```powershell
# Wait until database is healthy
docker-compose -f docker-compose.prod.yml ps database
```

### 5. Run Database Setup

```powershell
.\backend\scripts\setup_production_database.ps1
```

### 6. Start All Services

```powershell
docker-compose -f docker-compose.prod.yml up -d
```

## Post-Installation

### Viewing Logs

```powershell
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f database
```

### Stopping Services

```powershell
docker-compose -f docker-compose.prod.yml stop
```

### Starting Services

```powershell
docker-compose -f docker-compose.prod.yml start
```

### Restarting Services

```powershell
docker-compose -f docker-compose.prod.yml restart
```

## Troubleshooting

### Docker Desktop Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solution**:
1. Start Docker Desktop
2. Wait for it to fully start (whale icon in system tray)
3. Verify: `docker ps`

### Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
1. Find what's using the port:
   ```powershell
   netstat -ano | findstr :8000
   ```
2. Stop the conflicting service or change the port in `docker-compose.prod.yml`

### Database Connection Failed

**Error**: `could not connect to server`

**Solution**:
1. Check database container is running:
   ```powershell
   docker ps | findstr database
   ```
2. Check database logs:
   ```powershell
   docker-compose -f docker-compose.prod.yml logs database
   ```
3. Restart database:
   ```powershell
   docker-compose -f docker-compose.prod.yml restart database
   ```

### Frontend Not Loading

**Error**: Blank page or connection refused

**Solution**:
1. Check frontend container:
   ```powershell
   docker ps | findstr frontend
   ```
2. Check frontend logs:
   ```powershell
   docker-compose -f docker-compose.prod.yml logs frontend
   ```
3. Verify backend is accessible:
   ```powershell
   curl http://localhost:8000/health
   ```

### Out of Disk Space

**Error**: `no space left on device`

**Solution**:
1. Clean up Docker:
   ```powershell
   docker system prune -a
   ```
2. Remove unused volumes (be careful - this deletes data):
   ```powershell
   docker volume prune
   ```

### Permission Denied

**Error**: `Access is denied` or `Permission denied`

**Solution**:
1. Run PowerShell as Administrator
2. Check file permissions on installation directory
3. Ensure Docker Desktop has proper permissions

## Uninstallation

To completely remove TAMA38:

```powershell
.\uninstall.ps1
```

This will:
- Stop all containers
- Remove containers and images
- Optionally remove volumes (with confirmation)
- Clean up installation directory

## Support

For additional help:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review documentation in `docs/` directory
- Verify installation: `.\scripts\verify_installation.ps1`

## Security Considerations

1. **Change Default Passwords**: Update admin password and database password
2. **Generate Secure Keys**: Use strong, random keys for SECRET_KEY and JWT_SECRET_KEY
3. **Update CORS**: Set CORS_ORIGINS to your actual frontend URL
4. **Firewall**: Configure Windows Firewall to restrict access if needed
5. **Backup**: Regularly backup the database volume

## Next Steps

After successful installation:

1. Log in with admin credentials
2. Create additional users as needed
3. Configure projects and buildings
4. Set up agents and assign owners
5. Review system settings

Enjoy using TAMA38!

