# Automated EC2 Deployment Guide

## Overview

This guide explains how to use the automated deployment system for EC2. When you fix bugs or make changes, the system can automatically deploy only the changed files to EC2, restarting only the affected services.

## Quick Start

### 1. One-Time Setup

Configure your EC2 connection details:

```powershell
.\scripts\setup_ec2_config.ps1
```

Follow the prompts to enter:
- EC2 Public IP (e.g., `203.0.113.10`)
- EC2 User (default: `ec2-user`)
- SSH Key path (default: `C:\Users\aviel\.ssh\tama38-keypair.pem`)

This creates `.ec2-config.json` (automatically gitignored for security).

### 2. Deploy Changes

After fixing a bug or making changes:

```powershell
# Option 1: Auto-detect changed files from git (Recommended)
.\scripts\deploy_to_ec2.ps1 -Auto

# Option 2: Deploy specific files
.\scripts\deploy_to_ec2.ps1 -Files "backend/app/api/v1/auth.py"

# Option 3: Full deployment (for major changes)
.\scripts\deploy_to_ec2.ps1 -FullDeploy
```

## How It Works

### Smart Detection

The script automatically:
1. **Detects changed files** (from git or your input)
2. **Determines affected services**:
   - Backend files → Restart backend container
   - Frontend files → Restart frontend container
   - Docker config → Full restart
3. **Copies only changed files** to EC2
4. **Restarts only affected containers**
5. **Runs migrations** if backend changed

### Example Workflow

```powershell
# 1. Fix a bug in auth.py
# Edit: backend/app/api/v1/auth.py

# 2. Commit the change
git add backend/app/api/v1/auth.py
git commit -m "fix: resolve login authentication issue"

# 3. Auto-deploy
.\scripts\deploy_to_ec2.ps1 -Auto

# Output:
# Mode: Auto-detect changed files from git
# Found 1 file(s) to deploy:
#   - backend/app/api/v1/auth.py
# Services to restart:
#   ✓ Backend
# Step 1: Copying files to EC2...
# ✓ Files copied successfully!
# Step 2: Restarting services on EC2...
# ✓ Deployment completed successfully!
# Access the application:
#   Frontend: http://203.0.113.10:3000
#   Backend API: http://203.0.113.10:8000
```

## Cursor AI Auto-Deployment

When working on EC2-related fixes, Cursor AI will automatically deploy changes after commits.

**Auto-deployment triggers when:**
- Files match: `backend/**/*.py`, `frontend/src/**/*.{ts,tsx}`, `docker-compose.aws.yml`
- Commit messages mention: "EC2", "AWS", "deploy", "fix:", "bug:"
- Session context indicates EC2 work (mentions EC2 IP, deployment, etc.)

**To disable auto-deployment:**
- Set `AutoDeploy: false` in `.ec2-config.json`
- Or explicitly say: "Don't deploy to EC2"

## Deployment Modes

### Incremental Deployment (`-Auto` or `-Files`)

**Best for:** Bug fixes, small changes

- Copies only changed files
- Restarts only affected services
- Faster (typically 30-60 seconds)
- Less downtime

### Full Deployment (`-FullDeploy`)

**Best for:** Major changes, dependency updates

- Copies all files
- Rebuilds all containers
- Slower (typically 2-5 minutes)
- Use when updating `requirements.txt` or `package.json`

## Common Scenarios

### Scenario 1: Fix a Backend Bug

```powershell
# Fix the bug, commit, then:
.\scripts\deploy_to_ec2.ps1 -Auto
# Only backend restarts, frontend stays running
```

### Scenario 2: Fix a Frontend Bug

```powershell
# Fix the bug, commit, then:
.\scripts\deploy_to_ec2.ps1 -Auto
# Only frontend restarts, backend stays running
```

### Scenario 3: Update Dependencies

```powershell
# After updating requirements.txt or package.json:
.\scripts\deploy_to_ec2.ps1 -FullDeploy
# Full rebuild required
```

### Scenario 4: Deploy Multiple Files

```powershell
.\scripts\deploy_to_ec2.ps1 -Files `
  "backend/app/api/v1/auth.py", `
  "backend/app/core/config.py", `
  "frontend/src/services/auth.ts"
```

## Troubleshooting

### "EC2 Public IP not specified"

**Solution:** Run setup script:
```powershell
.\scripts\setup_ec2_config.ps1
```

### "SSH key not found"

**Solution:** Update `.ec2-config.json` with correct SSH key path, or run:
```powershell
.\scripts\setup_ec2_config.ps1
```

### "Permission denied (publickey)"

**Solution:** Fix SSH key permissions:
```powershell
icacls C:\Users\aviel\.ssh\tama38-keypair.pem /inheritance:r
icacls C:\Users\aviel\.ssh\tama38-keypair.pem /grant:r "$env:USERNAME`:R"
```

### Deployment Fails

1. **Check SSH connection:**
   ```powershell
   ssh -i C:\Users\aviel\.ssh\tama38-keypair.pem ec2-user@203.0.113.10
   ```

2. **Check EC2 instance status** in AWS Console

3. **Check Docker containers on EC2:**
   ```bash
   ssh -i ... ec2-user@203.0.113.10
   docker-compose -f docker-compose.aws.yml ps
   ```

4. **View logs:**
   ```bash
   docker-compose -f docker-compose.aws.yml logs backend
   docker-compose -f docker-compose.aws.yml logs frontend
   ```

## Files Created

- `scripts/deploy_to_ec2.ps1` - Smart automated deployment script
- `scripts/setup_ec2_config.ps1` - Configuration setup script
- `.cursor/rules/ec2_auto_deploy.cursorrules` - Cursor AI auto-deployment rules
- `.ec2-config.json` - Your EC2 configuration (gitignored)
- `.ec2-config.json.example` - Example configuration file

## Related Documentation

- [Deployment Scripts README](scripts/README_DEPLOYMENT.md) - Detailed script documentation
- [AWS Migration Guide](basic_migration_aws.md) - Complete EC2 setup guide
- [Cursor AI Rules](.cursor/rules/ec2_auto_deploy.cursorrules) - Auto-deployment rules

## Summary

✅ **One-time setup:** Run `setup_ec2_config.ps1`  
✅ **Deploy changes:** Run `deploy_to_ec2.ps1 -Auto`  
✅ **Cursor AI:** Automatically deploys when working on EC2 fixes  
✅ **Smart restart:** Only affected services restart  
✅ **Fast:** Incremental deployments take 30-60 seconds  

Happy deploying! 🚀

