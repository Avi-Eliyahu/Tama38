# SSH Setup for Windows - GitHub Authentication

**Quick guide for setting up SSH authentication on Windows**

---

## Status Check

✅ SSH is installed: OpenSSH_for_Windows_9.5p2  
✅ SSH key generated: `id_ed25519`  
✅ Public key ready for GitHub

---

## Next Steps

### 1. Add SSH Key to GitHub

**Option A: Using GitHub Website (Recommended)**

1. Go to https://github.com/settings/keys
2. Click **"New SSH key"**
3. **Title**: "TAMA38 Development - Windows"
4. **Key**: Paste your public key (already copied to clipboard)
5. Click **"Add SSH key"**

**Option B: Manual Copy**

Your public key is:
```
[Shown in terminal output above]
```

Copy the entire key (starts with `ssh-ed25519` and ends with your email)

---

### 2. Test SSH Connection

After adding the key to GitHub, test the connection:

```powershell
ssh -T git@github.com
```

**Expected output**:
```
Hi YOUR_USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
```

If you see this, SSH is working! ✅

---

### 3. Start SSH Agent (If Needed)

The SSH agent service might need to be started manually. Try these methods:

**Method 1: Start Service (Requires Admin)**
```powershell
# Run PowerShell as Administrator, then:
Start-Service ssh-agent
Set-Service -Name ssh-agent -StartupType Automatic
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

**Method 2: Manual Start (No Admin Required)**
```powershell
# Start agent manually
$env:SSH_AUTH_SOCK = ""
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

**Method 3: Use Git Credential Manager (Alternative)**

If SSH agent doesn't work, you can use HTTPS with Personal Access Token instead:

1. Go to https://github.com/settings/tokens
2. Generate new token (classic) with `repo` scope
3. Use token as password when pushing

---

### 4. Configure Git to Use SSH

When adding remote, use SSH URL:

```powershell
git remote add origin git@github.com:YOUR_USERNAME/tama38.git
```

**NOT** the HTTPS URL (`https://github.com/...`)

---

## Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution**:
```powershell
# Verify key is added
ssh-add -l

# If empty, add key
ssh-add $env:USERPROFILE\.ssh\id_ed25519

# Test connection
ssh -T git@github.com
```

### Issue: SSH Agent Won't Start

**Solution**: Use HTTPS with Personal Access Token instead:
1. Generate PAT on GitHub
2. Use HTTPS URL: `https://github.com/YOUR_USERNAME/tama38.git`
3. Use PAT as password when pushing

### Issue: "Host key verification failed"

**Solution**:
```powershell
# Remove old GitHub host key
ssh-keygen -R github.com

# Connect again (will prompt to add new key)
ssh -T git@github.com
# Type "yes" when prompted
```

---

## Verify Setup

Run these commands to verify everything is working:

```powershell
# Check SSH key exists
Test-Path $env:USERPROFILE\.ssh\id_ed25519.pub

# Check SSH agent
ssh-add -l

# Test GitHub connection
ssh -T git@github.com
```

---

## Quick Reference

**Your SSH Key Location**: `C:\Users\aviel\.ssh\id_ed25519`  
**Public Key**: `C:\Users\aviel\.ssh\id_ed25519.pub`  
**GitHub SSH Keys**: https://github.com/settings/keys

---

**Setup Complete!**

After adding the key to GitHub, you can use SSH URLs for git remotes.

