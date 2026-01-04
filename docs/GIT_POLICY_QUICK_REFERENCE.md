# Git Policy Quick Reference

**Quick command reference for TAMA38 Git workflow**

---

## Username Detection

Username is automatically detected from Git config:
```bash
git config user.name
# Example: "Aviel Cohen" → develop-aviel-cohen
```

To set/change:
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

---

## User Commands

### Commit
```
"commit changes"
"create commit"
"save changes"
```
- Auto-generates Conventional Commits message
- Commits to current branch (usually `develop-{username}`)

### Push
```
"push to remote"
"push changes"
```
- Explicit push request
- Also auto-pushes every 5 commits

### Tag Version
```
"tag version v1.2.0"
"release v1.2.0"
"create version tag v1.2.0"
```
- Requires review (AI or manual)
- Merges develop → main
- Creates tag and pushes

### Review Commands
```
"AI review"          # Request AI review before tagging
"manual review"      # Review manually before tagging
"confirm tag v1.2.0" # Confirm tagging after review
```

### Conflict Resolution
```
"AI resolve conflicts"  # AI-assisted conflict resolution
"manual resolve"       # Resolve conflicts manually
```

---

## Auto-Push Behavior

**Triggers**:
- ✅ Every 5 commits (automatic)
- ✅ User explicitly requests push

**Example**:
```
Commit 1: "feat: add feature A"
Commit 2: "fix: fix bug B"
Commit 3: "docs: update README"
Commit 4: "refactor: improve code"
Commit 5: "feat: add feature C"
→ Auto-push triggered! (5 commits reached)
```

---

## Conflict Resolution Flow

### When Conflicts Occur (Merge to Main)

1. **AI Detects Conflicts**:
   ```
   ⚠️ Conflicts detected when merging to main!
   Files: file1.tsx, file2.py
   ```

2. **User Chooses Method**:
   - `"AI resolve conflicts"` → AI analyzes and suggests fixes
   - `"manual resolve"` → User resolves manually

3. **AI Resolution Process**:
   - Analyzes conflict markers
   - Understands context from both branches
   - Shows diff preview
   - Waits for user confirmation
   - Applies resolution

4. **After Resolution**:
   - Continue with merge
   - Create tag
   - Push to remote

---

## Branch Lifecycle

```
1. Start: develop-{username} branch
   ↓
2. Work: Make changes, commit
   ↓
3. Auto-push: Every 5 commits
   ↓
4. Tag: User requests version tag
   ↓
5. Review: AI or manual review
   ↓
6. Merge: develop-{username} → main
   ↓
7. Check Conflicts: If conflicts, resolve
   ↓
8. Tag & Push: Create tag, push main and tag
   ↓
9. New Cycle: Create new develop-{username}
   ↓
10. Feature Branches: Create for next cycle
```

---

## Next Cycle Feature Branches

After merging to main, AI automatically creates:
- `feature/next-feature-1`
- `feature/next-feature-2`
- `feature/next-feature-3`

User can then:
- Switch to feature branch
- Work on features
- Merge back to develop-{username}

---

## Examples

### Daily Workflow
```
User: "Implement project editing modal"
AI: [Makes changes]

User: "commit changes"
AI: ✓ Committed: "feat(projects): add editing modal"
   Commits since last push: 1/5

[Continue working...]

User: "commit changes" (5th commit)
AI: ✓ Committed: "fix(ui): resolve modal styling"
   ✓ Auto-pushing (5 commits reached)...
   ✓ Pushed to origin/develop-aviel
```

### Version Release
```
User: "tag version v1.2.0"
AI: ✓ Release summary generated
   ⚠️ Review required: "AI review" or "manual review"?

User: "AI review"
AI: ✓ Review complete: Ready to merge
   Type "confirm tag v1.2.0" to proceed

User: "confirm tag v1.2.0"
AI: ✓ Merging develop-aviel → main...
   ✓ Checking conflicts... None found
   ✓ Tag v1.2.0 created
   ✓ Pushed main and tag
   ✓ Created new develop-aviel branch
   ✓ Created feature branches for next cycle
```

### Conflict Resolution
```
User: "tag version v1.2.0"
AI: ✓ Merging develop-aviel → main...
   ⚠️ Conflicts detected!
   Files: frontend/src/pages/ProjectDetail.tsx
   Choose: "AI resolve conflicts" or "manual resolve"

User: "AI resolve conflicts"
AI: ✓ Analyzing conflicts...
   ✓ Suggested resolution:
   [Shows diff preview]
   Type "apply resolution" to continue

User: "apply resolution"
AI: ✓ Conflicts resolved
   ✓ Continuing merge...
   ✓ Tag v1.2.0 created
```

---

## Troubleshooting

### Check Username
```bash
git config user.name
```

### Check Current Branch
```bash
git branch
```

### Check Commit Count
```bash
git log origin/develop-{username}..HEAD --oneline | wc -l
```

### Manual Push (if auto-push didn't trigger)
```
"push to remote"
```

---

**End of Quick Reference**

For detailed information, see `docs/CURSOR_GIT_POLICY.md`

