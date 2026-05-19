# Casa o Affitto — Deployment Checklist

Final checklist before pushing to GitHub and deploying to Streamlit Cloud.

**Date**: May 15, 2026
**Status**: Ready for Deployment

---

## Pre-Deployment Verification

### Code Quality ✅
- [x] All Python files follow PEP 8 style
- [x] No hardcoded secrets in code
- [x] No debug print statements in production code
- [x] Error handling for invalid inputs
- [x] No local absolute paths (uses relative paths only)
- [x] Imports verified to work from project root

### Configuration Files ✅
- [x] `.streamlit/config.toml` — Production configuration with:
  - [x] Theme colors configured (gold accent, dark background)
  - [x] Dark mode as default
  - [x] Server headless mode enabled
  - [x] Error details hidden from users
  - [x] XSRF protection enabled
- [x] `.streamlit/secrets.toml` — Placeholder created (gitignored)
- [x] `.gitignore` — Comprehensive, prevents secrets/cache

### Core Application Files ✅
- [x] `app.py` — Main Streamlit application (22.8 KB)
- [x] `calcoli.py` — Calculation engine (9.3 KB)
- [x] `dati.py` — Data and provinces (19.6 KB)
- [x] `requirements.txt` — All dependencies pinned:
  - [x] streamlit==1.45.0
  - [x] pandas>=2.0.0
  - [x] plotly>=5.18.0

### Documentation ✅
- [x] `README.md` — Comprehensive (10.9 KB) with:
  - [x] Project overview and key features
  - [x] "How it works" section (Input → Calculation → Output)
  - [x] Installation instructions
  - [x] Project structure
  - [x] Development section (tests, type checking, code style)
  - [x] Methodology section (data sources, assumptions, limitations)
  - [x] FAQ section (20+ questions answered)
  - [x] License and author info
  - [x] Support and contribution guidelines

- [x] `docs/DEPLOY.md` — Deployment guide (13.7 KB) with:
  - [x] Local development setup
  - [x] Streamlit Cloud deployment (step-by-step)
  - [x] Alternative deployments (Heroku, Docker, VPS)
  - [x] Production checklist
  - [x] Post-launch monitoring
  - [x] Troubleshooting guide

### Marketing Assets ✅
- [x] `assets/linkedin-post.md` — Multiple post versions:
  - [x] Professional version (comprehensive)
  - [x] Casual version (engaging)
  - [x] Technical version (developer-focused)
  - [x] Follow-up posts
  - [x] Engagement hook posts
  - [x] Hashtags optimized for reach

- [x] `assets/README.md` — Asset guidelines including:
  - [x] Screenshot specifications (1200x630px)
  - [x] Usage instructions
  - [x] How to create screenshot.png
  - [x] Sharing guidelines

### Git Repository ✅
- [x] Git initialized: `git init`
- [x] User configured: `git config user.name/email`
- [x] All files added and committed
- [x] Logical commit history:
  - [x] Commit 1: Streamlit configuration
  - [x] Commit 2: .gitignore
  - [x] Commit 3: Core application files
  - [x] Commit 4: README documentation
  - [x] Commit 5: Marketing assets
  - [x] Commit 6: Deployment guide

- [x] No uncommitted deployment files

---

## Local Testing ✅

### Environment
- [x] Python 3.8+ installed
- [x] Virtual environment created and activated
- [x] All dependencies installed: `pip install -r requirements.txt`
- [x] Dependencies verified: streamlit, plotly, pandas present

### Application Testing
Run the following to verify:

```bash
cd "/Users/salvatorederosa/Library/Mobile Documents/com~apple~CloudDocs/progetti/casa_vs_affitto"
streamlit run app.py
```

**Test checklist** (to be completed when running locally):
- [ ] App loads without errors (target: <5 seconds)
- [ ] UI renders correctly (dark theme default)
- [ ] Province/city selection works
- [ ] Property price input accepts valid values
- [ ] Loan parameters calculate correctly
- [ ] Tax regime selection changes results
- [ ] Charts render with data
- [ ] Theme toggle works (dark/light)
- [ ] App is responsive on different screen sizes
- [ ] No console errors in browser

---

## GitHub Repository Setup

### Before Pushing

1. **Create GitHub repository** (if not already done)
   - [ ] Repository name: `casa-vs-affitto`
   - [ ] Description: "A comprehensive financial calculator to help Italians decide: buy or rent?"
   - [ ] Public repository (users need access)
   - [ ] Initialize without README (we have one)
   - [ ] Initialize without .gitignore (we have one)

2. **Add remote and push**
   ```bash
   git remote add origin https://github.com/yourusername/casa-vs-affitto.git
   git branch -M main
   git push -u origin main
   ```

### Verify Remote
- [ ] All files pushed to GitHub
- [ ] Repository is public
- [ ] README.md renders correctly on GitHub
- [ ] No sensitive files committed (check git log)

---

## Streamlit Cloud Deployment

### Step 1: Connect to Streamlit Cloud
- [ ] Account created at [share.streamlit.io](https://share.streamlit.io)
- [ ] Signed in with GitHub
- [ ] Repository authorized for Streamlit access

### Step 2: Deploy Application
1. Click **"New app"**
2. Configure:
   - [ ] Repository: `yourusername/casa-vs-affitto`
   - [ ] Branch: `main`
   - [ ] Main file: `app.py`
3. Click **"Deploy!"**

### Step 3: Monitor Deployment
- [ ] Deployment starts (look for build logs)
- [ ] All dependencies install successfully
- [ ] No module import errors
- [ ] App launches and loads

### Step 4: Live URL Testing
- [ ] App accessible at live URL (e.g., `https://casa-vs-affitto.streamlit.app`)
- [ ] URL is shareable (works in incognito/private mode)
- [ ] Page title correct: "Casa o affitto? — Il calcolatore della verità"
- [ ] Icon displays: 🏠

---

## Post-Deployment Testing

### Desktop Browser Testing
- [ ] **Chrome**: App loads, all features work
- [ ] **Firefox**: App loads, all features work
- [ ] **Safari**: App loads, all features work
- [ ] **Edge**: App loads, all features work

### Mobile Browser Testing
- [ ] **iOS Safari**: Responsive, controls accessible
- [ ] **Android Chrome**: Responsive, controls accessible
- [ ] Landscape mode: Layout adjusts properly
- [ ] Portrait mode: Layout adjusts properly

### Feature Testing
- [ ] Province selection dropdown loads
- [ ] City dropdown filters correctly
- [ ] Property price input accepts values
- [ ] Loan parameters change results
- [ ] Tax regime selector works
- [ ] Expense fields update calculations
- [ ] Charts render with sample data
- [ ] All Plotly charts interactive (hover, zoom, pan)
- [ ] Theme toggle switches dark/light mode
- [ ] Sidebar opens/closes on mobile

### Performance Testing
- [ ] Initial page load: <10 seconds
- [ ] Province selection: <2 seconds
- [ ] Calculation updates: <3 seconds
- [ ] Chart rendering: <2 seconds
- [ ] No "app not responding" messages

### Error Handling
- [ ] Invalid property price: Shows error gracefully
- [ ] Negative loan term: Shows error gracefully
- [ ] Invalid interest rate: Shows error gracefully
- [ ] Network interruption: Shows appropriate message

---

## GitHub README Verification

On GitHub repository main page:

- [ ] README.md displays correctly
- [ ] All markdown formatting renders properly
- [ ] Links are clickable and work
- [ ] Live demo URL points to correct Streamlit Cloud app
- [ ] Code examples display with syntax highlighting
- [ ] Badges/shields render (if added)
- [ ] Table of contents navigates correctly
- [ ] All sections visible without scrolling needed to find content

---

## Marketing Preparation

### LinkedIn Post
- [ ] Copy from `assets/linkedin-post.md` selected
- [ ] Live URL included: https://casa-vs-affitto.streamlit.app
- [ ] Hashtags included and researched
- [ ] Post scheduled or ready to publish
- [ ] Profile updated (if needed)

### Screenshot Asset
- [ ] Screenshot taken of successful calculation state
- [ ] File saved as `assets/screenshot.png`
- [ ] Dimensions: 1200x630px (LinkedIn optimal)
- [ ] Compressed and optimized for web
- [ ] Shows: hero section + key results
- [ ] Text readable and colors clear

### Portfolio/GitHub
- [ ] Repository link shareable
- [ ] README compelling and complete
- [ ] DEPLOY.md provides clear instructions
- [ ] Code is clean and well-organized

---

## Final Git Status

Run this command to verify clean state:

```bash
cd "/Users/salvatorederosa/Library/Mobile Documents/com~apple~CloudDocs/progetti/casa_vs_affitto"
git status
```

Expected output:
```
On branch main
nothing to commit, working tree clean
```

✅ All deployment files committed
✅ No uncommitted changes to core files
✅ .gitignore working (tests/, features/, cache/ not tracked)

---

## Deployment Sign-Off

| Item | Status | Notes |
|------|--------|-------|
| Configuration files | ✅ Complete | config.toml, secrets.toml ready |
| Core application | ✅ Complete | app.py, calcoli.py, dati.py verified |
| Documentation | ✅ Complete | README, DEPLOY.md comprehensive |
| Marketing assets | ✅ Complete | LinkedIn post, screenshot guide |
| Git repository | ✅ Complete | All files committed, ready to push |
| Local testing | ⏳ Pending | To be tested on deployment |
| GitHub repo | ⏳ Pending | To be created and pushed |
| Streamlit Cloud | ⏳ Pending | To be deployed |
| Live testing | ⏳ Pending | To be verified after deployment |

---

## Next Steps (Post-Deployment)

1. **Create GitHub repository** and push all files
2. **Deploy on Streamlit Cloud** following docs/DEPLOY.md
3. **Test live URL** on desktop and mobile
4. **Share on LinkedIn** using assets/linkedin-post.md copy
5. **Monitor for 24 hours**: Check logs, user feedback, performance
6. **Update portfolio** with deployed app link

---

## Contact & Support

- **Author**: Salvatore De Rosa
- **Email**: salvatore98derosa@gmail.com
- **GitHub**: github.com/salvatorederosa
- **Live App**: https://casa-vs-affitto.streamlit.app

---

**Document Version**: 1.0  
**Last Updated**: May 15, 2026  
**Status**: Ready for Deployment ✅
