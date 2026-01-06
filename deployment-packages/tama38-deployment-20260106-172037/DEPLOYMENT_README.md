# TAMA38 Deployment Package - Quick Reference

This directory contains everything needed to deploy TAMA38 on a Windows machine.

## Files Overview

### Installation Files
- **`install.ps1`** - Main installation script (run this first)
- **`uninstall.ps1`** - Uninstallation script
- **`INSTALLATION_GUIDE.md`** - Detailed installation instructions
- **`env.production.template`** - Environment variables template

### Docker Configuration
- **`docker-compose.prod.yml`** - Production Docker Compose configuration
- **`backend/Dockerfile.prod`** - Production backend Docker image
- **`frontend/Dockerfile.prod`** - Production frontend Docker image
- **`frontend/nginx.conf`** - Nginx configuration for frontend

### Scripts
- **`backend/scripts/setup_production_database.ps1`** - Database setup script
- **`scripts/verify_installation.ps1`** - Installation verification script

### Source Code
- **`backend/`** - Backend application code
- **`frontend/` - Frontend application code

## Quick Start

1. **Extract** this package to your installation directory
2. **Open PowerShell as Administrator**
3. **Navigate** to the extracted directory
4. **Run**: `.\install.ps1`
5. **Follow** the on-screen instructions

## Default Credentials

After installation:
- **Email**: `admin@tama38.local`
- **Password**: `Admin123!@#`

**⚠️ Change these immediately after first login!**

## Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Common Commands

```powershell
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml stop

# Start services
docker-compose -f docker-compose.prod.yml start

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Verify installation
.\scripts\verify_installation.ps1

# Uninstall
.\uninstall.ps1
```

## Troubleshooting

See `INSTALLATION_GUIDE.md` for detailed troubleshooting steps.

## Support

For issues or questions:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Run verification: `.\scripts\verify_installation.ps1`
3. Review `INSTALLATION_GUIDE.md`

