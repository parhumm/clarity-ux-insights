# Security Guidelines

## 🔐 Sensitive Information - Never Commit These

**CRITICAL:** The following files and data must NEVER be committed to git or shared publicly:

### 1. Environment Configuration
- ❌ `.env` file (contains API tokens and credentials)
- ❌ `.env.local` or `.env.*.local` files
- ❌ Any file containing actual API tokens or passwords

### 2. Data Files
- ❌ `data/` directory (contains real user analytics data)
- ❌ `*.db` files (SQLite databases with collected metrics)
- ❌ `*.csv` files (exported analytics data)
- ❌ `*.json` files in `data/raw/` (API responses with real data)

### 3. Credentials
- ❌ Private keys (`*.key`, `*.pem`)
- ❌ Certificate files
- ❌ Any hardcoded API tokens in source code
- ❌ Authentication cookies

## ✅ What IS Safe to Commit

- ✅ Python source code (`.py` files)
- ✅ Configuration templates (`.env.example`)
- ✅ Database schema (`schema.sql`)
- ✅ Documentation (`*.md` files)
- ✅ Requirements file (`requirements.txt`)
- ✅ `.gitignore` file

## 🛡️ Required Environment Variables

Before running this project, you must configure these environment variables in your `.env` file:

```bash
# Required
CLARITY_API_TOKEN=your_jwt_token_here
CLARITY_PROJECT_ID=your_project_id

# Optional (have defaults)
API_BASE_URL=https://www.clarity.ms/export-data/api/v1
DB_PATH=data/clarity_data.db
```

**How to get these values:**

1. **CLARITY_API_TOKEN:**
   - Go to https://clarity.microsoft.com/
   - Navigate to your project Settings
   - Generate a Data Export API token
   - Scope required: `Data.Export`

2. **CLARITY_PROJECT_ID:**
   - Found in your Clarity project settings
   - Or in the URL when viewing your project

## 🚨 Security Best Practices

### 1. Environment Setup

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual credentials (use a secure editor)
nano .env  # or vim, vs code, etc.

# Verify .env is in .gitignore
git check-ignore .env
# Should output: .env
```

### 2. Check Before Committing

```bash
# Always check what you're about to commit
git status
git diff --staged

# Verify no sensitive files are staged
# Look for: .env, *.db, data/, *.csv, *.json
```

### 3. Verify .gitignore

Your `.gitignore` must include:
```gitignore
.env
.env.local
.env.*.local
data/
*.db
*.csv
*.json
secrets/
credentials/
*.key
*.pem
```

### 4. Accidental Commit Recovery

If you accidentally commit sensitive data:

```bash
# Remove file from staging
git reset HEAD .env

# Remove file from git history (if already committed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (only if you own the repo and no one else has cloned)
git push origin --force --all
```

**WARNING:** If the repository has already been pushed to a public location, assume all credentials in it are compromised. Immediately:
1. Revoke/regenerate API tokens
2. Change any passwords
3. Notify your team

## 🔍 Security Checklist Before Public Push

- [ ] `.env` file is NOT in git history
- [ ] No actual API tokens in source code
- [ ] No real data files committed
- [ ] `.gitignore` properly configured
- [ ] `.env.example` has only dummy values
- [ ] No client-specific information in code/docs
- [ ] Database files excluded
- [ ] No hardcoded credentials

## 📝 Data Privacy

This project collects analytics data from Microsoft Clarity, which includes:

- **Session metrics** (aggregated, no PII)
- **User behavior** (clicks, scrolls, navigation patterns)
- **Device/browser information**
- **Geographic data** (country-level)

**Important:**
- Clarity automatically hashes user IDs
- No personal identifiable information (PII) is stored
- All data is aggregated metrics
- Session recordings (if enabled) should be reviewed for sensitive information

## 🔗 Additional Resources

- **Microsoft Clarity Security:** https://learn.microsoft.com/en-us/clarity/setup-and-installation/security-and-privacy
- **Git Secrets Prevention:** https://github.com/awslabs/git-secrets
- **.gitignore Best Practices:** https://git-scm.com/docs/gitignore

## 📞 Reporting Security Issues

If you discover a security vulnerability in this project:

1. **DO NOT** create a public GitHub issue
2. Contact the repository maintainer privately
3. Provide details about the vulnerability
4. Allow time for a fix before public disclosure

---

**Last Updated:** 2025-11-25
**Maintainer:** Project Owner
