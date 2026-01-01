# SSH Troubleshooting Guide

## Issue: "Permission denied (publickey)"

This error means GitHub doesn't recognize your SSH key. Common causes:

### 1. Public Key Not Added to GitHub

**Check**: Have you added your public key to GitHub?

**Solution**:
1. Copy your public key:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
   ```

2. Go to https://github.com/settings/keys
3. Click "New SSH key"
4. Paste the key
5. Click "Add SSH key"

### 2. Wrong Key Format

**Check**: Make sure you copied the ENTIRE key, including:
- `ssh-ed25519` (key type)
- The long base64 string (key data)
- Your email (comment)

**Example of correct format**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILwsEw1QyfqjeCRVVvYgM0ZgpSs1a+xvvWMe9Ekp/bGJ avraham.eliyahu@example.com
```

### 3. SSH Agent Not Running

**Check**: Is SSH agent running?
```powershell
ssh-add -l
```

**If empty or error**: The agent isn't running.

**Solution A: Start SSH Agent (Requires Admin)**
```powershell
# Run PowerShell as Administrator
Start-Service ssh-agent
Set-Service -Name ssh-agent -StartupType Automatic
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

**Solution B: Use Key Directly (No Agent Needed)**
Git for Windows can use SSH keys directly without the agent. Just make sure:
- Your key is in `~/.ssh/id_ed25519`
- Public key is added to GitHub
- Test connection: `ssh -T git@github.com`

### 4. Wrong GitHub Username/Repository

**Check**: Are you using the correct GitHub username?

**Solution**: Verify your GitHub username matches:
```powershell
# Test connection
ssh -T git@github.com
```

### 5. Key Added to Wrong GitHub Account

**Check**: Did you add the key to the correct GitHub account?

**Solution**: 
- Verify you're logged into the right GitHub account
- Check https://github.com/settings/keys to see your keys

---

## Quick Fix Steps

1. **Verify key exists**:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
   ```

2. **Copy key to clipboard**:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
   ```

3. **Add to GitHub**: https://github.com/settings/keys

4. **Test connection**:
   ```powershell
   ssh -T git@github.com
   ```

5. **If still fails**: Try HTTPS with Personal Access Token instead

---

## Alternative: Use HTTPS with Personal Access Token

If SSH continues to cause issues, use HTTPS:

1. **Generate PAT**: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select `repo` scope
   - Copy token (save it!)

2. **Use HTTPS URL**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/tama38.git
   ```

3. **When pushing**: Use PAT as password

---

## Verify Your Setup

Run these commands to verify:

```powershell
# Check key exists
Test-Path $env:USERPROFILE\.ssh\id_ed25519.pub

# View public key
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

# Test GitHub connection
ssh -T git@github.com
```

**Expected success message**:
```
Hi YOUR_USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## Still Having Issues?

1. **Check GitHub status**: https://www.githubstatus.com/
2. **Verify key format**: Must be exactly as shown above
3. **Try HTTPS**: Often simpler on Windows
4. **Check firewall**: Make sure port 22 (SSH) isn't blocked

---

**Most Common Issue**: Public key not added to GitHub yet!

Make sure you:
1. Copied the ENTIRE public key
2. Added it to https://github.com/settings/keys
3. Clicked "Add SSH key" button

