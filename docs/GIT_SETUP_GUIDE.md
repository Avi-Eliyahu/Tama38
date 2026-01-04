# Git Setup & Usage Guide - TAMA38

**Complete guide for Git workflow, SSH setup, and repository management**

---

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [SSH Authentication](#ssh-authentication)
3. [Daily Workflow](#daily-workflow)
4. [Git Policy](#git-policy)
5. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Repository Information

- **Remote**: `git@github.com:Avi-Eliyahu/Tama38.git`
- **Main Branch**: `main`
- **Development Branch**: `develop-avraham-eliyahu`

### Verify Setup

```powershell
# Check current branch
git branch --show-current

# Check remote
git remote -v

# Test SSH connection
ssh -T git@github.com
```

---

## SSH Authentication

### Quick Setup

1. **Generate SSH Key** (if not already done):
   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add Key to GitHub**:
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste your public key (`~/.ssh/id_ed25519.pub`)

3. **Test Connection**:
   ```powershell
   ssh -T git@github.com
   ```

**For detailed Windows SSH setup, see**: [`WINDOWS_SSH_SETUP_COMPLETE.md`](./WINDOWS_SSH_SETUP_COMPLETE.md)

---

## Daily Workflow

### Making Changes

```powershell
# 1. Check current branch (should be develop-avraham-eliyahu)
git branch --show-current

# 2. Stage changes
git add .

# 3. Commit (using Conventional Commits format)
git commit -m "feat: add new feature"

# 4. Push (auto-push after 5 commits or on request)
git push origin develop-avraham-eliyahu
```

### Commit Message Format

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example**:
```
feat(auth): implement JWT refresh tokens

- Add refresh token endpoint
- Update token validation logic
- Add token rotation mechanism
```

---

## Git Policy

### Branching Strategy

- **`main`**: Production-ready code (tagged versions only)
- **`develop-{username}`**: Active development branch per user

### Version Tagging

When ready for release:
1. User requests: `"tag version v1.0.0"`
2. AI merges `develop-{username}` → `main`
3. Creates tag `v1.0.0`
4. Pushes to remote
5. Creates new `develop-{username}` branch

### Auto-Push Policy

- Automatic push after **5 commits**
- Automatic push on **milestone completion**
- Manual push on **user request**

**For complete Git policy details, see**:
- [`CURSOR_GIT_POLICY.md`](./CURSOR_GIT_POLICY.md) - Full policy
- [`GIT_POLICY_QUICK_REFERENCE.md`](./GIT_POLICY_QUICK_REFERENCE.md) - Quick reference

---

## Troubleshooting

### "Permission denied" when pushing

```powershell
# Test SSH connection
ssh -T git@github.com

# Should see: "Hi Avi-Eliyahu/Tama38! You've successfully authenticated..."
```

### Branch is behind remote

```powershell
git pull origin develop-avraham-eliyahu
```

### Undo last commit (before push)

```powershell
git reset --soft HEAD~1
```

### Check repository status

```powershell
git status
git log --oneline -10
```

---

## Related Documentation

- **SSH Setup**: [`WINDOWS_SSH_SETUP_COMPLETE.md`](./WINDOWS_SSH_SETUP_COMPLETE.md)
- **Git Policy**: [`CURSOR_GIT_POLICY.md`](./CURSOR_GIT_POLICY.md)
- **Quick Reference**: [`GIT_POLICY_QUICK_REFERENCE.md`](./GIT_POLICY_QUICK_REFERENCE.md)
- **Implementation Status**: [`IMPLEMENTATION_STATUS.md`](./IMPLEMENTATION_STATUS.md)

---

**Last Updated**: December 31, 2025

