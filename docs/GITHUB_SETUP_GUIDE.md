# GitHub Remote Setup Guide - TAMA38

**Initial setup guide for GitHub remote repository**

> **📚 Related Guides**:
> - **SSH Authentication**: See [`WINDOWS_SSH_SETUP_COMPLETE.md`](./WINDOWS_SSH_SETUP_COMPLETE.md)
> - **Git Workflow**: See [`GIT_SETUP_GUIDE.md`](./GIT_SETUP_GUIDE.md)
> - **Git Policy**: See [`CURSOR_GIT_POLICY.md`](./CURSOR_GIT_POLICY.md)

---

## Prerequisites

- GitHub account
- Git installed locally
- SSH key or Personal Access Token (PAT)

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name**: `tama38` (or your preferred name)
3. **Description**: "TAMA38 Urban Renewal Management Platform"
4. **Visibility**: Choose Public or Private
5. **DO NOT** check:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. Click **"Create repository"**

---

## Step 2: Choose Authentication Method

### Option A: SSH Key (Recommended)

#### Generate SSH Key

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# When prompted:
# - Press Enter for default file location
# - Enter passphrase (optional but recommended)
```

#### Add SSH Key to Agent

**Windows (PowerShell)**:
```powershell
# Start SSH agent
Start-Service ssh-agent

# Add key
ssh-add ~/.ssh/id_ed25519
```

**Mac/Linux**:
```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add key
ssh-add ~/.ssh/id_ed25519
```

#### Add Public Key to GitHub

```bash
# Copy public key to clipboard
# Windows:
cat ~/.ssh/id_ed25519.pub | clip

# Mac:
cat ~/.ssh/id_ed25519.pub | pbcopy

# Linux:
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard
```

**On GitHub**:
1. Go to https://github.com/settings/keys
2. Click **"New SSH key"**
3. **Title**: "TAMA38 Development"
4. **Key**: Paste your public key
5. Click **"Add SSH key"**

#### Test Connection

```bash
ssh -T git@github.com
# Should see: "Hi username! You've successfully authenticated..."
```

---

### Option B: Personal Access Token (PAT)

#### Create PAT

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Note**: "TAMA38 Development"
4. **Expiration**: Choose duration (90 days recommended)
5. **Scopes**: Check `repo` (all repo permissions)
6. Click **"Generate token"**
7. **COPY TOKEN IMMEDIATELY** (you won't see it again!)

#### Use PAT

When pushing, use token as password:
- **Username**: Your GitHub username
- **Password**: Your PAT (not your GitHub password)

---

## Step 3: Initialize Remote Repository

### Get Repository URL

After creating repository, GitHub shows:
- **SSH**: `git@github.com:YOUR_USERNAME/tama38.git`
- **HTTPS**: `https://github.com/YOUR_USERNAME/tama38.git`

**Use SSH if you set up SSH key, HTTPS if using PAT**

### Add Remote

```bash
# Navigate to project root
cd c:\projects\pinoy

# Add remote (replace YOUR_USERNAME)
git remote add origin git@github.com:YOUR_USERNAME/tama38.git

# Verify remote added
git remote -v
# Should show:
# origin  git@github.com:YOUR_USERNAME/tama38.git (fetch)
# origin  git@github.com:YOUR_USERNAME/tama38.git (push)
```

---

## Step 4: Create and Push Branches

### Create Main Branch

```bash
# Ensure you're on main (or create it)
git checkout -b main

# Push main branch
git push -u origin main
```

### Create User Develop Branch

```bash
# Replace 'aviel' with your username
git checkout -b develop-aviel

# Push develop branch
git push -u origin develop-aviel
```

### Set Default Branch on GitHub

1. Go to repository → **Settings** → **Branches**
2. Under **"Default branch"**, click **"Switch to another branch"**
3. Select `develop-aviel` (or your develop branch)
4. Click **"Update"**
5. Confirm switch

---

## Step 5: Configure Branch Protection (Optional)

### Protect Main Branch

1. Go to repository → **Settings** → **Branches**
2. Click **"Add rule"**
3. **Branch name pattern**: `main`
4. Check:
   - ✅ Require a pull request before merging
   - ✅ Require approvals: 1
   - ✅ Require status checks to pass before merging
   - ✅ Include administrators
5. Click **"Create"**

### Develop Branch

No protection needed (for development flexibility)

---

## Step 6: Verify Setup

### Test Connection

```bash
# Fetch from remote
git fetch origin

# Check branches
git branch -a
# Should show:
# * develop-aviel
#   main
#   remotes/origin/develop-aviel
#   remotes/origin/main
```

### Test Push

```bash
# Make a small change
echo "# Test" >> README.md

# Commit
git add README.md
git commit -m "test: verify remote connection"

# Push
git push origin develop-aviel

# Check GitHub - should see your commit
```

---

## Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution**:
```bash
# Test SSH connection
ssh -T git@github.com

# If fails, check SSH key is added
ssh-add -l

# Re-add key
ssh-add ~/.ssh/id_ed25519
```

### Issue: "Authentication failed" (HTTPS)

**Solution**:
- Use Personal Access Token instead of password
- Or switch to SSH authentication

### Issue: "Remote already exists"

**Solution**:
```bash
# Remove existing remote
git remote remove origin

# Add again
git remote add origin git@github.com:YOUR_USERNAME/tama38.git
```

### Issue: "Branch protection prevents push"

**Solution**:
- You're trying to push to protected `main` branch
- Push to `develop-{username}` instead
- Merge to `main` via tagging workflow

---

## Next Steps

After setup:
1. ✅ Remote configured
2. ✅ Branches created
3. ✅ Ready to use Cursor Git commands

**Try it**:
```
User: "commit changes"
User: "push to remote"
User: "tag version v1.0.0"
```

---

**Setup Complete!**

For Git policy details, see `docs/CURSOR_GIT_POLICY.md`

