# Cursor Git Policy for TAMA38

**Version:** 1.0  
**Last Updated:** December 31, 2025

---

## Overview

Git workflow policy integrated with Cursor AI. All operations require explicit user requests except automatic pushes after milestones.

---

## Branch Strategy

### Per-User Develop Branch

- **Pattern**: `develop-{username}` (e.g., `develop-aviel`)
- **Username Detection**: Automatically detected from `git config user.name` (lowercase, spaces replaced with hyphens)
- **Purpose**: User's personal development integration branch
- **Lifecycle**: 
  1. Work on features → commit to `develop-{username}`
  2. On tagging: merge `develop-{username}` → `main`
  3. After merge: automatically create new `develop-{username}` branch
  4. AI creates feature branches for next development cycle

### Branch Types

- **`main`**: Production-ready code, protected
- **`develop-{username}`**: User's development branch (one per user)
- **`feature/*`**: Feature branches (auto-created by AI after main merge)

---

## User Prompt Commands

### 1. Commit Operation

**Command**: `"commit changes"` or `"create commit"`

**AI Behavior**:
1. Analyze changes since last commit
2. Generate Conventional Commits format message
3. Stage changes (respect `.gitignore`)
4. Create commit
5. Display summary

**Commit Format**:
```
<type>(<scope>): <subject>

<body>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Example**:
```
User: "commit changes"

AI: ✓ Analyzing changes...
   ✓ Commit: "feat(projects): add modal-based editing system
   
   - Created reusable Modal component
   - Added ProjectEditForm and BuildingEditForm
   - Integrated edit modals into detail pages"
   
   ✓ Committed: abc1234
```

---

### 2. Push Operation (Automatic)

**Automatic Push Triggers**:
- **Every 5 commits** (counted since last push)
- After user explicitly requests: `"push to remote"`

**AI Behavior**:
1. Check current branch (`develop-{username}`)
2. Verify remote configured
3. Count commits since last push
4. If 5+ commits OR user requested: push to remote (no conflict check)
5. Display result with commit count

**Example**:
```
User: "commit changes" (5th commit since last push)

AI: ✓ Committed: abc1234
   ✓ Auto-pushing (5 commits since last push)...
   ✓ Pushed to origin/develop-aviel
```

**Conflict Handling**: 
- Regular pushes: No conflict check
- Merge to main: Check for conflicts, present to user, offer resolution

---

### 3. Version Tagging Operation

**Command**: `"tag version v1.2.0"` or `"release v1.2.0"`

**AI Behavior**:
1. Verify version format (SemVer)
2. Check current branch is `develop-{username}`
3. Generate release summary
4. **REQUIRE REVIEW** (user chooses):
   - `"AI review"` → AI analyzes changes
   - `"manual review"` → User reviews manually
5. After review approval:
   - Merge `develop-{username}` → `main`
   - **Check for conflicts**:
     - If conflicts detected: Present to user with details
     - Offer AI-assisted resolution or manual resolution
     - Wait for user confirmation after resolution
   - Create annotated tag on `main`
   - Push `main` and tag to remote
   - Create new `develop-{username}` branch
   - Create feature branches for next development cycle

**Example**:
```
User: "tag version v1.2.0"

AI: ✓ Version format: v1.2.0 ✓
   ✓ Current branch: develop-aviel
   ✓ Analyzing changes...
   
   📋 Release Summary (v1.2.0):
   - feat(projects): modal-based editing system
   - feat(db): database seeding script
   - fix(ui): RTL layout issues
   
   ⚠️  Review required before merging to main
   
   Choose review method:
   - Type "AI review" for automated review
   - Type "manual review" to review yourself

User: "AI review"

AI: ✓ AI Review Results:
   - No breaking changes detected
   - All tests pass
   - Code quality: Good
   - Ready to merge
   
   Type "confirm tag v1.2.0" to proceed

User: "confirm tag v1.2.0"

AI: ✓ Merging develop-aviel → main...
   ✓ Checking for conflicts... None found
   ✓ Creating tag v1.2.0...
   ✓ Pushing main and tag...
   ✓ Creating new develop-aviel branch...
   ✓ Creating feature branches for next cycle...
   ✓ Release v1.2.0 complete!
```

---

## Change Tracking

### Commit-to-Commit Tracking

AI maintains internal log of:
- Files changed between commits
- Feature descriptions
- Bug descriptions
- Change summaries

**Used for**:
- Generating commit messages
- Creating release summaries
- AI review analysis

---

## GitHub Remote Setup

### Step 1: Create Repository

1. Go to https://github.com/new
2. Name: `tama38`
3. Choose Public/Private
4. **DO NOT** initialize with files
5. Click "Create repository"

### Step 2: Configure Authentication

#### SSH (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Start agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub | clip

# Add to GitHub: Settings → SSH Keys → New SSH Key
# Test: ssh -T git@github.com
```

#### Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate token (classic) with `repo` scope
3. Save token securely

### Step 3: Initialize Remote

```bash
# Add remote
git remote add origin git@github.com:YOUR_USERNAME/tama38.git

# Verify
git remote -v

# Create main branch
git checkout -b main
git push -u origin main

# Create user develop branch
git checkout -b develop-aviel  # Replace 'aviel' with your username
git push -u origin develop-aviel

# Set default branch to develop-{username} on GitHub
```

### Step 4: Configure Branch Protection

**On GitHub**:
1. Settings → Branches
2. Add rule for `main`:
   - ✅ Require pull request reviews
   - ✅ Require status checks
   - ✅ Include administrators
3. `develop-{username}`: No protection (for development)

---

## Workflow Examples

### Daily Development

```
1. User: "Implement project editing"
   → AI makes changes

2. User: "commit changes"
   → AI: Creates commit on develop-aviel
   → Auto-push (if milestone reached)

3. Continue development...
```

### Version Release

```
1. User: "tag version v1.2.0"
   → AI: Generates summary, requests review

2. User: "AI review"
   → AI: Reviews changes, reports results

3. User: "confirm tag v1.2.0"
   → AI: Merges develop-aviel → main
   → Creates tag v1.2.0
   → Pushes to remote
   → Creates new develop-aviel branch
   → Creates feature branches
```

---

## AI Assistant Rules

### When Making Changes

1. **Track Changes**: Maintain internal log of all changes
2. **Never Auto-Commit**: Wait for user request
3. **Respect .gitignore**: Never stage ignored files
4. **Clean Code**: Remove debug logs before commit
5. **Conventional Commits**: Always use format

### Change Summary Format

```
## Changes Since Last Commit

### Files Modified:
- path/to/file1.tsx (modified)
- path/to/file2.py (new)

### Features Added:
- Feature description 1
- Feature description 2

### Bug Fixes:
- Bug description 1

### Other Changes:
- Documentation updates
```

---

## Error Handling

### No Changes
```
User: "commit changes"
AI: ⚠️ No changes detected. Working directory clean.
```

### Not on Develop Branch
```
User: "tag version v1.2.0"
AI: ⚠️ You're on 'feature/xyz', not 'develop-aviel'.
    Switching to develop-aviel...
```

### Merge Conflicts
```
AI: ⚠️ Conflicts detected when merging to main!
    
    Files with conflicts:
    - frontend/src/pages/ProjectDetail.tsx
    - backend/app/api/projects.py
    
    Choose resolution method:
    - Type "AI resolve conflicts" for AI-assisted resolution
    - Type "manual resolve" to resolve manually
    
    After resolution, I'll continue with tagging.
```

**AI-Assisted Conflict Resolution**:
- AI analyzes conflicts
- Suggests resolutions based on context
- Shows diff preview
- User confirms before applying

**Manual Resolution**:
- AI provides conflict details
- User resolves manually
- User confirms when done

---

## Quick Reference

### User Commands

| Command | Action |
|---------|--------|
| `"commit changes"` | Create commit with auto-generated message |
| `"push to remote"` | Explicit push (otherwise auto-push) |
| `"tag version v1.2.0"` | Create version tag (requires review) |
| `"AI review"` | Request AI review before tagging |
| `"manual review"` | Review manually before tagging |
| `"confirm tag v1.2.0"` | Confirm and execute tagging |
| `"show git status"` | Display current git status |
| `"show changes"` | Display changes since last commit |

### Automatic Behaviors

- ✅ Auto-push every 5 commits
- ✅ Auto-push when user explicitly requests
- ✅ Auto-create develop branch after merge
- ✅ Auto-create feature branches for next cycle after merge
- ✅ Conflict check only on merge to main
- ✅ Username detection from git config

---

**End of Policy**

For detailed Git usage, see `docs/how_to_use_git_TAMA38.md`
