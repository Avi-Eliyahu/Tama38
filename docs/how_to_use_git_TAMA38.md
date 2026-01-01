# TAMA38 Git Usage Guide

**Version:** 1.0  
**Last Updated:** December 31, 2025  
**Project:** TAMA38 Urban Renewal Management Platform

---

## Table of Contents

1. [Remote Git Repository Setup](#1-remote-git-repository-setup)
2. [Branching Strategy](#2-branching-strategy)
3. [Commit Message Guidelines](#3-commit-message-guidelines)
4. [Tagging & Versioning Policy](#4-tagging--versioning-policy)
5. [Cursor Project Rules](#5-cursor-project-rules)
6. [Daily Workflow](#6-daily-workflow)
7. [Code Review Process](#7-code-review-process)
8. [Emergency Hotfix Process](#8-emergency-hotfix-process)
9. [Release Process](#9-release-process)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Remote Git Repository Setup

### 1.1 What We Need From You

To establish a remote Git repository, please provide:

1. **Repository URL** (choose one):
   - GitHub: `https://github.com/YOUR_ORG/tama38.git` or `git@github.com:YOUR_ORG/tama38.git`
   - GitLab: `https://gitlab.com/YOUR_ORG/tama38.git` or `git@gitlab.com:YOUR_ORG/tama38.git`
   - Bitbucket: `https://bitbucket.org/YOUR_ORG/tama38.git` or `git@bitbucket.org:YOUR_ORG/tama38.git`
   - Azure DevOps: `https://dev.azure.com/YOUR_ORG/tama38/_git/tama38`
   - Self-hosted: Provide the URL

2. **Authentication Method**:
   - SSH key (recommended for security)
   - Personal Access Token (PAT)
   - Username/Password (less secure, not recommended)

3. **Repository Access**:
   - Public or Private repository?
   - Who should have access? (team members, stakeholders)

4. **Default Branch Name**:
   - `main` (recommended) or `master`?

### 1.2 Initial Remote Setup (After You Provide Details)

Once you provide the repository URL, run these commands:

```bash
# Add remote repository
git remote add origin <YOUR_REPOSITORY_URL>

# Verify remote was added
git remote -v

# Push existing code to remote (first time)
git branch -M main  # Rename branch to 'main' if needed
git push -u origin main

# Set upstream tracking
git branch --set-upstream-to=origin/main main
```

### 1.3 SSH Key Setup (Recommended)

If using SSH authentication:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard (Windows)
cat ~/.ssh/id_ed25519.pub | clip

# Add public key to your Git hosting service (GitHub/GitLab/etc.)
# Then test connection:
ssh -T git@github.com  # or git@gitlab.com, etc.
```

---

## 2. Branching Strategy

### 2.1 Branch Types

We use **Git Flow** with the following branch types:

#### **main** (Production/Stable)
- **Purpose**: Production-ready code
- **Protection**: Protected branch (no direct pushes)
- **Merges**: Only from `develop` or `hotfix/*` branches
- **Tags**: All releases are tagged here

#### **develop** (Development/Integration)
- **Purpose**: Integration branch for completed features
- **Protection**: Protected branch (no direct pushes)
- **Merges**: From `feature/*`, `bugfix/*`, or `hotfix/*` branches
- **Status**: Should always be deployable to staging

#### **feature/** (Feature Development)
- **Naming**: `feature/TAMA38-123-short-description`
- **Purpose**: New features, enhancements
- **Source**: Branch from `develop`
- **Merge**: Back to `develop` via Pull Request
- **Examples**:
  - `feature/TAMA38-101-project-wizard-ui`
  - `feature/TAMA38-102-whatsapp-integration`
  - `feature/TAMA38-103-document-signing`

#### **bugfix/** (Bug Fixes)
- **Naming**: `bugfix/TAMA38-456-fix-login-error`
- **Purpose**: Fix bugs found in `develop` or `main`
- **Source**: Branch from `develop` or `main` (depending on severity)
- **Merge**: Back to `develop` (and `main` if critical)
- **Examples**:
  - `bugfix/TAMA38-201-fix-building-list-empty`
  - `bugfix/TAMA38-202-cors-error-api`

#### **hotfix/** (Critical Production Fixes)
- **Naming**: `hotfix/TAMA38-789-critical-security-fix`
- **Purpose**: Urgent fixes for production issues
- **Source**: Branch from `main`
- **Merge**: Back to both `main` AND `develop`
- **Examples**:
  - `hotfix/TAMA38-301-security-patch-auth`
  - `hotfix/TAMA38-302-database-connection-fix`

#### **release/** (Release Preparation)
- **Naming**: `release/v1.2.0` or `release/phase-1-complete`
- **Purpose**: Prepare for a new release version
- **Source**: Branch from `develop`
- **Merge**: Back to both `main` (with tag) AND `develop`
- **Use**: Final testing, version bumping, changelog updates

### 2.2 Branch Naming Convention

Format: `<type>/<TICKET>-<short-description>`

- **Type**: `feature`, `bugfix`, `hotfix`, `release`
- **TICKET**: Optional ticket number (e.g., `TAMA38-123`)
- **Description**: Short, kebab-case description (max 50 chars)

**Good Examples:**
```
feature/TAMA38-101-project-wizard-step-2
bugfix/TAMA38-201-fix-uuid-serialization
hotfix/TAMA38-301-security-patch
release/v1.0.0-phase1
```

**Bad Examples:**
```
feature/my-new-feature          # Missing ticket number
bugfix/fix                     # Too vague
feature/TAMA38-101-this-is-a-very-long-description-that-exceeds-fifty-characters  # Too long
```

### 2.3 Branch Lifecycle

```
1. Create branch from appropriate source
   git checkout develop
   git pull origin develop
   git checkout -b feature/TAMA38-123-my-feature

2. Develop and commit changes
   git add .
   git commit -m "feat: implement building list API"

3. Push branch to remote
   git push -u origin feature/TAMA38-123-my-feature

4. Create Pull Request (PR) on Git hosting platform

5. After PR approval and merge, delete local branch
   git checkout develop
   git pull origin develop
   git branch -d feature/TAMA38-123-my-feature
```

---

## 3. Commit Message Guidelines

### 3.1 Commit Message Format

We follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(projects): add project wizard step 2` |
| `fix` | Bug fix | `fix(buildings): resolve empty buildings list for agents` |
| `docs` | Documentation changes | `docs(readme): update installation instructions` |
| `style` | Code style changes (formatting, no logic change) | `style(frontend): format code with prettier` |
| `refactor` | Code refactoring (no bug fix, no feature) | `refactor(auth): simplify JWT validation logic` |
| `perf` | Performance improvements | `perf(api): optimize database query for buildings` |
| `test` | Adding or updating tests | `test(projects): add unit tests for project creation` |
| `chore` | Maintenance tasks, dependencies | `chore(deps): update axios to v1.6.0` |
| `build` | Build system changes | `build(docker): update docker-compose configuration` |
| `ci` | CI/CD changes | `ci(github): add automated testing workflow` |

### 3.3 Scope (Optional)

Scope indicates the area of code affected:

- `auth` - Authentication & authorization
- `projects` - Project management
- `buildings` - Building management
- `units` - Unit management
- `owners` - Owner/tenant management
- `wizard` - Project creation wizard
- `interactions` - CRM interactions
- `documents` - Document management
- `approvals` - Approval workflow
- `tasks` - Task management
- `dashboard` - Dashboard
- `agents` - Agent mobile app
- `api` - API endpoints
- `frontend` - Frontend components
- `backend` - Backend services
- `db` - Database migrations
- `docker` - Docker configuration
- `docs` - Documentation

### 3.4 Subject Line Rules

- **Required**: Present tense, imperative mood ("add" not "added" or "adds")
- **Required**: No period at the end
- **Required**: Max 72 characters
- **Required**: Capitalize first letter
- **Recommended**: Start with lowercase if scope is present

**Good Examples:**
```
feat(projects): add building list to project detail page
fix(auth): resolve login timeout issue
docs(readme): update quick start guide
refactor(api): simplify UUID serialization logic
```

**Bad Examples:**
```
feat: Added new feature                    # Wrong tense
fix(buildings): fixed the bug.             # Wrong tense, period at end
feat(projects): Add building list to project detail page with many details # Too long
FEAT: add feature                          # Wrong case
```

### 3.5 Body (Optional but Recommended)

- **When to use**: For complex changes that need explanation
- **Format**: Blank line after subject, then detailed explanation
- **Content**: What changed, why it changed, any breaking changes

**Example:**
```
feat(projects): add building list to project detail page

Previously, the project detail page only showed a placeholder text.
This commit implements the full buildings list functionality:
- Loads buildings filtered by project ID
- Displays building cards with status and signature progress
- Shows loading and empty states
- Links to individual building detail pages

This improves user experience by providing immediate visibility
of project buildings without navigating to a separate page.
```

### 3.6 Footer (Optional)

Used for:
- **Breaking changes**: `BREAKING CHANGE: <description>`
- **Issue references**: `Closes #123`, `Fixes #456`, `Refs #789`

**Example:**
```
feat(api): change authentication endpoint

BREAKING CHANGE: The /auth/login endpoint now requires email
instead of username. Update all API clients accordingly.

Closes #123
Refs #456
```

### 3.7 Complete Commit Examples

**Simple commit:**
```bash
git commit -m "feat(projects): add project wizard step 2"
```

**Complex commit:**
```bash
git commit -m "fix(buildings): resolve empty buildings list for agents

Previously, agents could only see buildings explicitly assigned to them.
This fix modifies the role-based filter to also include unassigned
buildings (assigned_agent_id is None), allowing agents to see all
available buildings.

Changes:
- Updated list_buildings endpoint filter logic
- Added OR condition for unassigned buildings
- Removed debug instrumentation logs

Closes #201"
```

**Multi-file commit:**
```bash
git add frontend/src/pages/ProjectDetail.tsx
git add frontend/src/services/buildings.ts
git commit -m "feat(projects): implement buildings list on project detail page

- Add loadBuildings function to ProjectDetail component
- Display building cards with status and signature progress
- Add loading and empty states
- Link to building detail pages"
```

---

## 4. Tagging & Versioning Policy

### 4.1 Version Number Format

We use **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, major feature releases
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, backward-compatible patches

**Examples:**
- `v1.0.0` - Initial Phase 1 release
- `v1.1.0` - Phase 1 with new features (e.g., agent mobile app)
- `v1.1.1` - Bug fixes only
- `v2.0.0` - Phase 2 release (AWS migration, Twilio integration)

### 4.2 Tag Naming Convention

Format: `v<MAJOR>.<MINOR>.<PATCH>` or `v<MAJOR>.<MINOR>.<PATCH>-<PRERELEASE>`

**Examples:**
```
v1.0.0                    # Stable release
v1.0.0-alpha.1           # Alpha pre-release
v1.0.0-beta.2            # Beta pre-release
v1.0.0-rc.1              # Release candidate
v1.1.0                    # Minor release
v1.1.1                    # Patch release
v2.0.0                    # Major release
```

### 4.3 When to Tag

- **Major Release**: Phase completion, major architectural changes
- **Minor Release**: Significant new features, milestone completion
- **Patch Release**: Bug fixes, security patches, minor improvements
- **Pre-release**: Alpha/beta testing, release candidates

### 4.4 Creating Tags

```bash
# Create annotated tag (recommended)
git tag -a v1.0.0 -m "Release v1.0.0: Phase 1 Complete

Features:
- Project management with wizard
- Building, unit, and owner management
- Agent mobile application
- Document management
- Approval workflow
- Dashboard and reporting

Breaking Changes: None"

# Push tag to remote
git push origin v1.0.0

# Push all tags
git push origin --tags

# List tags
git tag -l

# View tag details
git show v1.0.0

# Delete tag (if needed)
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### 4.5 Tagging Workflow

1. **Before Release**:
   ```bash
   # Create release branch
   git checkout -b release/v1.1.0 develop
   
   # Update version numbers in code
   # - Update package.json (frontend)
   # - Update __version__.py (backend)
   # - Update CHANGELOG.md
   
   # Commit version bump
   git commit -m "chore: bump version to 1.1.0"
   
   # Create tag
   git tag -a v1.1.0 -m "Release v1.1.0"
   ```

2. **Merge to main**:
   ```bash
   git checkout main
   git merge --no-ff release/v1.1.0
   git push origin main
   git push origin v1.1.0
   ```

3. **Merge back to develop**:
   ```bash
   git checkout develop
   git merge --no-ff release/v1.1.0
   git push origin develop
   ```

4. **Delete release branch**:
   ```bash
   git branch -d release/v1.1.0
   git push origin --delete release/v1.1.0
   ```

### 4.6 Version Tracking in Code

Update version in these files:

**Frontend** (`frontend/package.json`):
```json
{
  "version": "1.1.0"
}
```

**Backend** (`backend/app/__version__.py`):
```python
__version__ = "1.1.0"
```

**Documentation** (`TAMA38_Design_document.md`):
```markdown
**Version:** 1.1
```

---

## 5. Cursor Project Rules

### 5.1 Cursor-Specific Git Configuration

Add to `.cursorrules` or project settings:

```markdown
## Git Integration Rules

1. **Auto-commit**: Disabled (manual commits only)
2. **Commit on Save**: Never
3. **Branch Detection**: Automatic
4. **Staging**: Manual staging required
5. **Commit Message**: Use Conventional Commits format
6. **Pre-commit Hooks**: Run linters and tests before commit
```

### 5.2 Cursor AI Assistant Rules

When AI assistant makes changes:

1. **Review before committing**: Always review AI-generated code
2. **Test before commit**: Run tests and verify functionality
3. **Meaningful commits**: Group related changes together
4. **No auto-commit**: Never commit automatically
5. **Instrumentation cleanup**: Remove debug logs before committing

### 5.3 File Exclusions

Files that should NOT be committed (already in `.gitignore`):

```
# Debug logs
.cursor/debug.log
*.log

# Environment files
.env
.env.local
.env.*.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Build outputs
dist/
build/
*.egg-info/

# Database
*.db
*.sqlite
*.sqlite3

# OS files
.DS_Store
Thumbs.db
```

### 5.4 Cursor Workflow Integration

**When using Cursor AI:**

1. **Before AI changes**: Create a feature branch
   ```bash
   git checkout -b feature/TAMA38-123-ai-implementation
   ```

2. **After AI changes**: Review and stage selectively
   ```bash
   git status
   git add <specific-files>
   git commit -m "feat(scope): AI-generated feature implementation"
   ```

3. **Clean up**: Remove instrumentation, fix linting
   ```bash
   git add .
   git commit -m "style: remove debug logs and fix linting"
   ```

---

## 6. Daily Workflow

### 6.1 Starting Work

```bash
# Update local develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/TAMA38-123-my-feature

# Verify branch
git branch
```

### 6.2 During Development

```bash
# Check status frequently
git status

# Stage specific files
git add frontend/src/pages/MyPage.tsx
git add backend/app/api/v1/my_api.py

# Commit with meaningful message
git commit -m "feat(projects): add new feature"

# Push to remote (creates remote branch)
git push -u origin feature/TAMA38-123-my-feature
```

### 6.3 Before Committing

**Checklist:**
- [ ] Code compiles without errors
- [ ] Linting passes (`npm run lint` or `flake8`)
- [ ] Tests pass (if applicable)
- [ ] Debug logs removed
- [ ] Commit message follows conventions
- [ ] Only related changes in commit
- [ ] No sensitive data (passwords, keys)

### 6.4 Syncing with Remote

```bash
# Fetch latest changes
git fetch origin

# Rebase on latest develop (before PR)
git checkout develop
git pull origin develop
git checkout feature/TAMA38-123-my-feature
git rebase develop

# Resolve conflicts if any
git add <resolved-files>
git rebase --continue

# Force push after rebase (only on feature branches)
git push --force-with-lease origin feature/TAMA38-123-my-feature
```

### 6.5 End of Day

```bash
# Commit and push work in progress
git add .
git commit -m "WIP: work in progress on feature"
git push origin feature/TAMA38-123-my-feature

# Or stash changes
git stash push -m "WIP: end of day work"
```

---

## 7. Code Review Process

### 7.1 Pull Request (PR) Guidelines

**PR Title Format:**
```
<type>(<scope>): <description>
```

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring
- [ ] Performance improvement

## Related Ticket
Closes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Tested on local environment

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

### 7.2 PR Review Checklist

**For Author:**
- [ ] PR title follows convention
- [ ] Description is complete
- [ ] All CI checks pass
- [ ] Code is self-reviewed
- [ ] No debug code or console.logs
- [ ] Documentation updated if needed

**For Reviewer:**
- [ ] Code quality and style
- [ ] Logic correctness
- [ ] Performance considerations
- [ ] Security implications
- [ ] Test coverage
- [ ] Documentation completeness

### 7.3 PR Merge Strategy

**Merge Options:**
- **Squash and Merge** (recommended for feature branches)
- **Merge Commit** (for release branches)
- **Rebase and Merge** (for small, linear changes)

**After Merge:**
```bash
# Update local develop
git checkout develop
git pull origin develop

# Delete local feature branch
git branch -d feature/TAMA38-123-my-feature
```

---

## 8. Emergency Hotfix Process

### 8.1 When to Use Hotfix

- Critical production bug
- Security vulnerability
- Data corruption issue
- Service outage

### 8.2 Hotfix Workflow

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/TAMA38-301-critical-fix

# 2. Make fix and commit
git add .
git commit -m "fix(api): resolve critical database connection issue

Critical fix for production database connection timeout.
Implements connection pooling and retry logic.

BREAKING CHANGE: None
Closes #301"

# 3. Push and create PR
git push -u origin hotfix/TAMA38-301-critical-fix

# 4. After PR approval, merge to main
git checkout main
git merge --no-ff hotfix/TAMA38-301-critical-fix
git push origin main

# 5. Tag the hotfix
git tag -a v1.0.1 -m "Hotfix v1.0.1: Critical database fix"
git push origin v1.0.1

# 6. Merge back to develop
git checkout develop
git merge --no-ff hotfix/TAMA38-301-critical-fix
git push origin develop

# 7. Delete hotfix branch
git branch -d hotfix/TAMA38-301-critical-fix
git push origin --delete hotfix/TAMA38-301-critical-fix
```

---

## 9. Release Process

### 9.1 Release Checklist

**Before Release:**
- [ ] All features complete and tested
- [ ] All bugs fixed
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated
- [ ] Tests pass
- [ ] Security scan completed

**Release Steps:**

1. **Create release branch:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.1.0
   ```

2. **Update version numbers:**
   - `frontend/package.json`
   - `backend/app/__version__.py`
   - `TAMA38_Design_document.md`
   - `CHANGELOG.md`

3. **Final testing:**
   ```bash
   # Run all tests
   npm test
   pytest

   # Build and verify
   docker-compose build
   docker-compose up -d
   ```

4. **Create tag:**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0: Phase 1 Complete"
   ```

5. **Merge to main:**
   ```bash
   git checkout main
   git merge --no-ff release/v1.1.0
   git push origin main
   git push origin v1.1.0
   ```

6. **Merge back to develop:**
   ```bash
   git checkout develop
   git merge --no-ff release/v1.1.0
   git push origin develop
   ```

7. **Delete release branch:**
   ```bash
   git branch -d release/v1.1.0
   git push origin --delete release/v1.1.0
   ```

### 9.2 CHANGELOG.md Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-31

### Added
- Agent mobile application with dashboard and leads management
- Buildings list on project detail page
- Document signing workflow improvements

### Changed
- Updated building API to show unassigned buildings to agents
- Improved error handling in project wizard

### Fixed
- Fixed empty buildings list for agent users
- Fixed UUID serialization in document upload endpoint
- Fixed CORS errors in interactions API

## [1.0.0] - 2025-12-15

### Added
- Initial Phase 1 release
- Project management with wizard
- Building, unit, and owner management
- Document management
- Approval workflow
- Dashboard and reporting
```

---

## 10. Troubleshooting

### 10.1 Common Issues

**Issue: "Your branch is behind 'origin/main'"**
```bash
# Fetch latest changes
git fetch origin

# Rebase your branch
git rebase origin/main

# Or merge
git merge origin/main
```

**Issue: "Merge conflict"**
```bash
# See conflicted files
git status

# Resolve conflicts manually
# Then:
git add <resolved-files>
git commit -m "fix: resolve merge conflicts"
```

**Issue: "Accidentally committed to wrong branch"**
```bash
# Move last commit to correct branch
git log --oneline -1  # Note commit hash
git reset HEAD~1      # Remove from current branch
git checkout correct-branch
git cherry-pick <commit-hash>
```

**Issue: "Need to undo last commit"**
```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Discard changes, undo commit
git reset --hard HEAD~1  # WARNING: Destructive!
```

**Issue: "Pushed wrong commit"**
```bash
# Create revert commit (safe)
git revert <commit-hash>
git push origin <branch>

# Or force push (dangerous, only on feature branches)
git reset --hard <previous-commit>
git push --force-with-lease origin <branch>
```

### 10.2 Useful Git Commands

```bash
# View commit history
git log --oneline --graph --all

# See what changed
git diff
git diff --staged

# Find when a bug was introduced
git bisect start
git bisect bad
git bisect good <commit-hash>

# Stash changes temporarily
git stash
git stash pop
git stash list

# See file history
git log --follow -- <file-path>

# Find commits by message
git log --grep="fix"

# Clean untracked files
git clean -fd

# See branch relationships
git log --graph --oneline --all --decorate
```

### 10.3 Getting Help

- **Git Documentation**: https://git-scm.com/doc
- **Conventional Commits**: https://www.conventionalcommits.org/
- **Semantic Versioning**: https://semver.org/
- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/

---

## Appendix A: Quick Reference

### Branch Commands
```bash
# Create and switch
git checkout -b feature/TAMA38-123-name

# Switch branch
git checkout develop

# List branches
git branch -a

# Delete branch
git branch -d feature/TAMA38-123-name
```

### Commit Commands
```bash
# Stage all changes
git add .

# Stage specific file
git add path/to/file

# Commit
git commit -m "type(scope): message"

# Amend last commit
git commit --amend
```

### Tag Commands
```bash
# Create tag
git tag -a v1.0.0 -m "Release message"

# Push tag
git push origin v1.0.0

# List tags
git tag -l

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

---

## Appendix B: Git Configuration

### Recommended Git Config

```bash
# Set user name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set editor
git config --global core.editor "code --wait"  # VS Code
# or
git config --global core.editor "nano"

# Enable color output
git config --global color.ui auto

# Set default merge strategy
git config --global pull.rebase false

# Set push default
git config --global push.default simple

# Enable credential helper (Windows)
git config --global credential.helper wincred

# Set line ending handling
git config --global core.autocrlf true  # Windows
git config --global core.autocrlf input  # Mac/Linux
```

---

**End of Git Usage Guide**

For questions or updates to this guide, please contact the project maintainer or update this document via a Pull Request.

