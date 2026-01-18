# EC2 Deployment Scripts

This directory contains scripts for deploying the TAMA38 application to AWS EC2.

## Quick Start

### 1. Initial Setup

First, configure your EC2 connection details:

```powershell
.\scripts\setup_ec2_config.ps1
```

This creates `.ec2-config.json` with your EC2 IP, user, and SSH key path.

### 2. Automated Deployment

After fixing bugs or making changes, deploy automatically:

```powershell
# Auto-detect changed files from git
.\scripts\deploy_to_ec2.ps1 -Auto

# Or deploy specific files
.\scripts\deploy_to_ec2.ps1 -Files "backend/app/api/v1/auth.py"

# Or full deployment
.\scripts\deploy_to_ec2.ps1 -FullDeploy
```

## Scripts Overview

### `deploy_to_ec2.ps1` - Smart Automated Deployment

**Purpose:** Deploy only changed files to EC2, restarting only affected services.

**Features:**
- Auto-detects changed files from git
- Smart service restart (only affected containers)
- Incremental deployment (copies only changed files)
- Automatic migration handling
- Error handling and status reporting

**Usage:**
```powershell
# Auto-detect from git
.\scripts\deploy_to_ec2.ps1 -Auto

# Deploy specific files
.\scripts\deploy_to_ec2.ps1 -Files "backend/app/api/v1/auth.py", "frontend/src/pages/Login.tsx"

# Full deployment
.\scripts\deploy_to_ec2.ps1 -FullDeploy

# Override EC2 IP (if not in config)
.\scripts\deploy_to_ec2.ps1 -Auto -EC2PublicIP "54.123.45.67"
```

**How it works:**
1. Detects which files changed (from git or parameters)
2. Determines which services are affected (backend/frontend/both)
3. Copies only changed files to EC2 via SCP
4. Restarts only affected Docker containers
5. Runs migrations if backend changed
6. Reports deployment status

### `deploy_aws.ps1` - Full Deployment Script

**Purpose:** Complete deployment of entire application to EC2.

**Usage:**
```powershell
.\scripts\deploy_aws.ps1 -EC2PublicIP "YOUR_EC2_PUBLIC_IP" -EC2User "ec2-user"
```

**When to use:**
- Initial deployment
- Major changes requiring full rebuild
- After updating dependencies

### `setup_ec2_config.ps1` - Configuration Setup

**Purpose:** Interactive setup of EC2 connection configuration.

**Usage:**
```powershell
.\scripts\setup_ec2_config.ps1
```

**Creates:** `.ec2-config.json` (gitignored, contains sensitive data)

## Cursor AI Integration

When working on EC2-related fixes, Cursor AI will automatically deploy changes after commits. See `.cursor/rules/ec2_auto_deploy.cursorrules` for details.

**Auto-deployment triggers:**
- Backend code changes (`backend/**/*.py`)
- Frontend code changes (`frontend/src/**/*.{ts,tsx}`)
- Docker configuration changes (`docker-compose.aws.yml`)
- Script changes (`scripts/**/*.py`)

## Configuration File

`.ec2-config.json` structure:
```json
{
  "EC2PublicIP": "YOUR_EC2_PUBLIC_IP",
  "EC2User": "ec2-user",
  "SSHKey": "C:\\Users\\aviel\\.ssh\\tama38-keypair.pem",
  "AutoDeploy": true
}
```

**Security:** This file is in `.gitignore` and should never be committed.

## Deployment Modes

### Incremental Deployment (Recommended)
- Copies only changed files
- Restarts only affected services
- Faster deployment
- Less downtime

### Full Deployment
- Copies all files
- Rebuilds all containers
- Longer deployment time
- Use for major changes or initial setup

## Troubleshooting

### SSH Connection Issues
```powershell
# Test SSH connection
ssh -i C:\Users\aviel\.ssh\tama38-keypair.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### Permission Denied
```powershell
# Fix SSH key permissions (Windows)
icacls C:\Users\aviel\.ssh\tama38-keypair.pem /inheritance:r
icacls C:\Users\aviel\.ssh\tama38-keypair.pem /grant:r "$env:USERNAME`:R"
```

### Deployment Fails
1. Check SSH connection
2. Verify EC2 instance is running
3. Check Docker containers on EC2: `docker-compose -f docker-compose.aws.yml ps`
4. View logs: `docker-compose -f docker-compose.aws.yml logs`

## Examples

### Example 1: Fix a Bug
```powershell
# 1. Fix bug in auth.py
# 2. Commit
git commit -m "fix: resolve login issue"

# 3. Auto-deploy
.\scripts\deploy_to_ec2.ps1 -Auto
```

### Example 2: Deploy Multiple Files
```powershell
.\scripts\deploy_to_ec2.ps1 -Files `
  "backend/app/api/v1/auth.py", `
  "backend/app/core/config.py", `
  "frontend/src/services/auth.ts"
```

### Example 3: Full Rebuild After Dependency Update
```powershell
# After updating requirements.txt or package.json
.\scripts\deploy_to_ec2.ps1 -FullDeploy
```

## Best Practices

1. **Use incremental deployment** for bug fixes and small changes
2. **Use full deployment** for major changes or dependency updates
3. **Test locally first** before deploying to EC2
4. **Commit changes** before deploying (or use -Auto flag)
5. **Monitor deployment** output for errors
6. **Verify deployment** by checking application URLs

## Related Documentation

- [AWS Migration Guide](../basic_migration_aws.md) - Complete EC2 setup guide
- [Cursor AI Rules](../.cursor/rules/ec2_auto_deploy.cursorrules) - Auto-deployment rules

