# Pre-Push Security Checklist

**⚠️ CRITICAL: Run this checklist BEFORE pushing to GitHub!**

## Step 1: Remove Sensitive Files

```bash
# Remove ALL sensitive files
rm -f .env
rm -f credentials.json
rm -f token.json
rm -f data/preferences.json

# Verify they're gone
ls -la | grep -E "\.env$|credentials|token"
ls -la data/

# Expected: Should show NO sensitive files
```

## Step 2: Verify .gitignore is Working

```bash
# Check what git will track
git status

# Expected output should NOT include:
# - .env
# - credentials.json
# - token.json
# - data/preferences.json
# - __pycache__/ directories
```

## Step 3: Check for Accidentally Staged Files

```bash
# See what's staged for commit
git diff --staged

# If you see any sensitive data, unstage it:
git reset HEAD <filename>
```

## Step 4: Verify No Sensitive Data in Files

```bash
# Search for potential API keys in all files
grep -r "AIza" . --exclude-dir=.git --exclude="*.md" 2>/dev/null || echo "✅ No Google AI keys found"
grep -r "OPENWEATHER_API_KEY=" . --exclude-dir=.git --exclude=".env.example" 2>/dev/null || echo "✅ No weather keys found"

# Check for hardcoded project numbers
grep -r "225866861023" . --exclude-dir=.git --exclude="*.md" 2>/dev/null || echo "✅ No project numbers found"

# Expected: Should only find placeholders in .env.example and docs
```

## Step 5: Clean Up Cache Files

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# Remove macOS files
find . -name ".DS_Store" -delete 2>/dev/null

echo "✅ Cache cleaned"
```

## Step 6: Review Git History (CRITICAL!)

```bash
# Check if sensitive files were EVER committed
git log --all --full-history -- .env
git log --all --full-history -- credentials.json
git log --all --full-history -- token.json

# Expected: Should show "fatal: ambiguous argument" or no results
# If you see commit history: THESE FILES ARE IN YOUR GIT HISTORY!
```

### If Sensitive Files Are in Git History:

**⚠️ WARNING: Deleting files doesn't remove them from git history!**

You have two options:

**Option A: Start Fresh (Recommended)**
```bash
# 1. Backup your current code
cp -r . ../weatheritbetter-backup

# 2. Delete .git directory
rm -rf .git

# 3. Initialize new repo
git init
git add .
git commit -m "Initial commit: WeatherItBetter AI Agent"

# 4. Create new GitHub repo and push
git remote add origin <your-new-repo-url>
git push -u origin main
```

**Option B: Remove from History (Advanced)**
```bash
# Use git-filter-repo (must install first)
# pip install git-filter-repo

git filter-repo --path .env --invert-paths
git filter-repo --path credentials.json --invert-paths
git filter-repo --path token.json --invert-paths
```

## Step 7: Final Safety Check

```bash
# List ALL files that will be pushed
git ls-files

# Review the list carefully
# Should NOT include:
# - .env
# - credentials.json
# - token.json
# - data/preferences.json
# - Any __pycache__ directories
```

## Step 8: Safe to Push!

Once all checks pass:

```bash
# Stage all changes
git add .

# Commit
git commit -m "Add WeatherItBetter AI outfit recommendation agent"

# Push to GitHub
git push origin main
```

## Post-Push Verification

After pushing, immediately check your GitHub repo:

1. **Go to your repo on GitHub**
2. **Browse the files** - verify no `.env` or `credentials.json`
3. **Use GitHub search** - search for "AIza" or "OPENWEATHER" in the repo
4. **Check commit history** - make sure no sensitive data in any commit

## If You Find Exposed Credentials on GitHub:

**🚨 IMMEDIATE ACTION REQUIRED:**

1. **Revoke ALL exposed API keys immediately:**
   - Google AI: https://aistudio.google.com/app/apikey (delete and create new)
   - OpenWeatherMap: https://home.openweathermap.org/api_keys (delete and create new)
   - Google Cloud: https://console.cloud.google.com/apis/credentials (delete OAuth credentials)

2. **Delete the GitHub repository**
3. **Follow "Option A: Start Fresh" above**
4. **Generate NEW API keys**
5. **Push clean version**

## Additional GitHub Security Settings

After pushing, configure these in your GitHub repo:

1. **Settings → Branches → Branch protection rules**
   - Protect main branch
   - Require pull request reviews

2. **Settings → Security → Secret scanning**
   - Enable if available

3. **Add .gitattributes** (optional)
   ```bash
   echo "*.env filter=git-crypt diff=git-crypt" > .gitattributes
   echo "credentials.json filter=git-crypt diff=git-crypt" >> .gitattributes
   ```

---

## Quick Command Sequence

For quick verification, run this:

```bash
# One-liner safety check
rm -f .env credentials.json token.json data/preferences.json && \
echo "=== Checking git status ===" && \
git status && \
echo "=== Checking for API keys ===" && \
grep -r "AIza" . --exclude-dir=.git --exclude="*.md" --exclude-dir=docs 2>/dev/null | grep -v ".env.example" || echo "✅ No keys found" && \
echo "=== Checking git history ===" && \
git log --all --full-history -- .env 2>&1 | head -1 && \
echo "=== Ready to push! ==="
```

---

**Remember:** Once something is on GitHub, assume it's public forever. Even if you delete it, someone might have already seen it!

**Better safe than sorry! 🔒**
