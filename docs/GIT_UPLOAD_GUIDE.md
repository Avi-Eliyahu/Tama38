# Git Upload Guide - TAMA38 Repository

## ✅ Current Status

**Repository**: `git@github.com:Avi-Eliyahu/Tama38.git`  
**SSH Authentication**: ✅ Working  
**Current Branch**: `develop-avraham-eliyahu`  
**Remote Branches**: `main`, `develop-avraham-eliyahu`

---

## 📋 Pre-Upload Checklist

### ✅ Completed:
- [x] Git repository initialized
- [x] Remote configured (`origin`)
- [x] SSH authentication working
- [x] Branches created (`main`, `develop-avraham-eliyahu`)
- [x] `.gitignore` configured
- [x] Sensitive files excluded (SSH keys, temp files)

### ⚠️ Files Excluded from Commit:
- `key`, `key.pub` (SSH keys - security)
- `drive-download-*.zip` (temporary files)
- `.env` files (environment variables)
- `node_modules/`, `__pycache__/` (dependencies)
- `.cursor/debug.log` (debug logs)

---

## 🚀 Upload Process

### Step 1: Review Files to Commit

```powershell
# See what will be committed
git status

# See detailed list
git status --short
```

### Step 2: Add Files to Staging

**Option A: Add All Files (Recommended for initial commit)**
```powershell
git add .
```

**Option B: Add Specific Directories**
```powershell
git add backend/
git add frontend/
git add docs/
git add scripts/
git add docker-compose.yml
git add README.md
git add TAMA38_Design_document.md
# ... etc
```

### Step 3: Review Staged Files

```powershell
# See what's staged
git status

# See detailed diff (if modifying existing files)
git diff --cached
```

### Step 4: Create Initial Commit

**According to Git Policy (Conventional Commits):**

```powershell
git commit -m "feat: initial project setup

- Backend API (FastAPI, SQLAlchemy, Alembic)
- Frontend React application (TypeScript, Tailwind)
- Docker Compose configuration
- Database models and migrations
- Authentication and authorization
- Project management (Projects, Buildings, Units, Owners)
- Mobile agent application
- Multi-language support (i18n)
- Documentation and design documents"
```

### Step 5: Push to Remote

**Push to develop branch:**
```powershell
git push -u origin develop-avraham-eliyahu
```

**After pushing, verify:**
```powershell
git log --oneline -5
git branch -a
```

---

## 📝 Commit Message Format

Following **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance tasks

**Example:**
```
feat(auth): implement JWT authentication

- Add JWT token generation
- Implement refresh token mechanism
- Add protected route middleware
- Update login/logout endpoints
```

---

## 🔄 Workflow After Initial Upload

### Daily Development:

1. **Make changes**
2. **Stage changes:**
   ```powershell
   git add .
   ```
3. **Commit:**
   ```powershell
   git commit -m "feat: add new feature"
   ```
4. **Push (auto after 5 commits or on request):**
   ```powershell
   git push origin develop-avraham-eliyahu
   ```

### When Ready for Version Tag:

1. **User requests tag:**
   ```
   "tag version v1.0.0"
   ```
2. **AI will:**
   - Merge `develop-avraham-eliyahu` → `main`
   - Create tag `v1.0.0`
   - Push to remote
   - Create new `develop-avraham-eliyahu` branch

---

## 🛡️ Security Notes

**Never commit:**
- SSH private keys (`key`, `id_ed25519`, etc.)
- Environment files (`.env`, `.env.local`)
- API keys or secrets
- Database files (`*.db`, `*.sqlite`)
- Personal credentials

**Always check:**
```powershell
git status
```
Before committing!

---

## 🐛 Troubleshooting

### "Permission denied" when pushing:
```powershell
# Test SSH connection
ssh -T git@github.com

# Should see: "Hi Avi-Eliyahu/Tama38! You've successfully authenticated..."
```

### "Branch is behind remote":
```powershell
# Pull latest changes
git pull origin develop-avraham-eliyahu
```

### "Large file detected":
- GitHub has 100MB file size limit
- Use Git LFS for large files:
  ```powershell
  git lfs install
  git lfs track "*.zip"
  git add .gitattributes
  ```

### Undo last commit (before push):
```powershell
git reset --soft HEAD~1
```

---

## 📊 Repository Structure

```
TAMA38/
├── backend/          # Python FastAPI backend
├── frontend/         # React TypeScript frontend
├── docs/            # Documentation
├── scripts/         # Utility scripts
├── samples/         # Sample data files
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## ✅ Verification Commands

```powershell
# Check repository status
git status

# Check remote configuration
git remote -v

# Check branches
git branch -a

# Check SSH connection
ssh -T git@github.com

# View commit history
git log --oneline -10

# Check what will be committed
git diff --cached
```

---

## 🎯 Next Steps After Upload

1. ✅ Verify files on GitHub web interface
2. ✅ Check branch protection rules (if needed)
3. ✅ Set up CI/CD (future)
4. ✅ Configure branch protection (optional)
5. ✅ Add collaborators (if needed)

---

**Ready to upload!** Follow Step 1-5 above to push your code to GitHub.

