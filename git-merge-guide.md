# Merging feature/docx-converter to main

## Method 1: PowerShell Commands

```powershell
# 1. Navigate to project directory
cd "D:\Users\alexp\dev\email-parser"

# 2. Verify current branch
git branch --show-current
# Should show: feature/docx-converter

# 3. Switch to main branch
git checkout main

# 4. Pull latest changes from remote (if any)
git pull origin main

# 5. Merge the feature branch
git merge feature/docx-converter

# 6. Push merged changes to remote
git push origin main

# 7. Optional: Delete the feature branch (locally)
git branch -d feature/docx-converter

# 8. Optional: Delete the feature branch (remotely)
git push origin --delete feature/docx-converter
```

## Method 2: VS Code GUI (Beginner-Friendly)

### Step 1: Open Source Control
1. Open VS Code in your project folder
2. Click the **Source Control** icon in the left sidebar (looks like a branch symbol)

### Step 2: Switch to Main Branch
1. Look at the bottom-left of VS Code - you'll see current branch name
2. Click on the branch name (should show `feature/docx-converter`)
3. Select **"main"** from the dropdown list
4. VS Code will switch to the main branch

### Step 3: Merge Using Command Palette
1. Press `Ctrl + Shift + P` to open Command Palette
2. Type: `Git: Merge Branch`
3. Select it from the list
4. Choose `feature/docx-converter` from the branch list
5. VS Code will merge the branch

### Step 4: Push Changes
1. In Source Control panel, you'll see changes ready to commit
2. Click the **"..."** menu (three dots)
3. Select **"Push"**
4. This uploads your merged changes to GitHub/remote

### Step 5: Clean Up (Optional)
1. Press `Ctrl + Shift + P` again
2. Type: `Git: Delete Branch`
3. Select `feature/docx-converter`
4. Choose to delete both local and remote branches

## Method 3: VS Code Terminal (Hybrid Approach)

1. In VS Code, press `Ctrl + `` (backtick) to open terminal
2. Run the PowerShell commands above directly in VS Code's terminal

## What to Expect:

- **If successful**: You'll see "Merge successful" or similar message
- **If conflicts**: VS Code will show conflict markers - resolve them manually
- **After merge**: Your main branch will contain all DOCX converter features

## Verification Commands:

```powershell
# Check you're on main
git branch --show-current

# Verify merge completed
git log --oneline -5

# Check all files are present
ls email_parser/converters/
```

## Additional Tips for Beginners:

### Before Merging (Safety Check):
```powershell
# Save your current work
git add .
git commit -m "Save current work before merge"

# Check what will be merged
git diff main feature/docx-converter --stat
```

### If Something Goes Wrong:
```powershell
# Undo the merge (if you haven't pushed yet)
git reset --hard HEAD~1

# Or go back to a specific commit
git reset --hard <commit-hash>
```

### Best Practices:
1. **Always commit your changes** before switching branches
2. **Pull latest main** before merging to avoid conflicts
3. **Test after merging** to ensure everything works
4. **Don't delete branches immediately** - wait until you're sure the merge is good

**Recommendation for beginners**: Use VS Code GUI method - it's more visual and forgiving!

---

*Created: 2025-07-01*  
*Project: Email Parser - Phase 2 DOCX Converter Integration*  
*Status: Ready for merge to main*