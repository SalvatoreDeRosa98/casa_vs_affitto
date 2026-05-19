# Deployment Guide — Casa o Affitto

Complete guide for deploying Casa o Affitto to production on Streamlit Cloud.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Alternative: Self-Hosted Deployment](#alternative-self-hosted-deployment)
4. [Production Checklist](#production-checklist)
5. [Post-Launch Monitoring](#post-launch-monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

- **Python 3.8+** — Check: `python --version`
- **pip** — Check: `pip --version`
- **git** — Check: `git --version`
- **GitHub account** — For pushing code

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/casa-vs-affitto.git
cd casa-vs-affitto
```

### Step 2: Create Virtual Environment

```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Locally

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

### Step 5: Test All Features

- [ ] Select different provinces
- [ ] Change property prices
- [ ] Adjust loan parameters
- [ ] Switch tax regimes
- [ ] View all charts
- [ ] Test dark/light theme toggle
- [ ] Resize window (mobile responsiveness)
- [ ] Export PDF (if feature enabled)
- [ ] Compare scenarios
- [ ] Run sensitivity analysis

---

## Streamlit Cloud Deployment

### Recommended: Streamlit Cloud (Free Tier)

Streamlit Cloud is the fastest, easiest way to deploy Streamlit apps.

#### Step 1: Prepare GitHub Repository

1. **Create public GitHub repository** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: casa-vs-affitto application"
   git branch -M main
   git remote add origin https://github.com/yourusername/casa-vs-affitto.git
   git push -u origin main
   ```

2. **Verify repository structure**
   - `app.py` — Main application
   - `calcoli.py` — Calculation engine
   - `dati.py` — Data module
   - `requirements.txt` — Dependencies
   - `.streamlit/config.toml` — Configuration
   - `README.md` — Documentation

3. **Ensure .gitignore exists** (never commit secrets)
   ```
   .streamlit/secrets.toml
   __pycache__/
   *.pyc
   .env
   ```

#### Step 2: Deploy on Streamlit Cloud

1. Visit [share.streamlit.io](https://share.streamlit.io)

2. Sign in with GitHub (create account if needed)

3. Click **"New app"**

4. Configure:
   - **Repository**: Select `yourusername/casa-vs-affitto`
   - **Branch**: `main`
   - **Main file path**: `app.py`

5. Click **"Deploy!"**

The app will be available at: `https://casa-vs-affitto.streamlit.app`

#### Step 3: Configure Environment

**For any secrets or environment variables:**

1. Go to app settings (⋯ menu → Settings)
2. Click **"Secrets"**
3. Add any required secrets (currently none, but placeholder exists)

---

### Alternative: Deploy from Repo Template

If you've enabled the "Deploy Button" in README:

1. Click [![Deploy](https://share.streamlit.io/images/streamlit_badge_black_white.svg)](https://share.streamlit.io/new)
2. Paste repository URL: `https://github.com/yourusername/casa-vs-affitto`
3. Deploy automatically

---

## Alternative: Self-Hosted Deployment

### Option A: Heroku

#### Prerequisites
- Heroku account (create at [heroku.com](https://www.heroku.com))
- Heroku CLI installed

#### Steps

1. **Create Procfile** in repository root:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create runtime.txt**:
   ```
   python-3.11.0
   ```

3. **Deploy**:
   ```bash
   heroku create casa-vs-affitto
   git push heroku main
   ```

4. **View logs**:
   ```bash
   heroku logs --tail
   ```

5. **Open app**:
   ```bash
   heroku open
   ```

### Option B: Docker (Any Cloud Provider)

#### Build Docker Image

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build image**:
   ```bash
   docker build -t casa-vs-affitto .
   ```

3. **Run locally**:
   ```bash
   docker run -p 8501:8501 casa-vs-affitto
   ```

#### Deploy to Cloud

**Google Cloud Run:**
```bash
gcloud run deploy casa-vs-affitto \
  --source . \
  --platform managed \
  --memory 512Mi \
  --timeout 3600
```

**AWS Lightsail/ECS** — Consult AWS documentation for containerized app deployment.

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name casa-vs-affitto \
  --image casa-vs-affitto:latest \
  --ports 8501 \
  --cpu 1 --memory 0.5
```

### Option C: VPS (DigitalOcean, Linode, etc.)

1. **SSH into server**
2. **Install Python 3.11+**
3. **Clone repository** and install dependencies
4. **Use systemd service** or **supervisor** to keep app running
5. **Use Nginx** as reverse proxy
6. **Configure SSL** with Let's Encrypt

See Streamlit documentation for detailed VPS setup.

---

## Production Checklist

Before going live, verify:

### Code Quality
- [ ] All Python code follows PEP 8 style
- [ ] Type hints present (mypy passes)
- [ ] No hardcoded secrets in code
- [ ] No debug print statements
- [ ] Error handling for invalid inputs
- [ ] Tests pass (if applicable)

### Configuration
- [ ] `.streamlit/config.toml` has production settings
- [ ] Dark theme configured as default
- [ ] Server headless mode enabled
- [ ] Error details hidden from users
- [ ] XSRF protection enabled

### Data & Assets
- [ ] All data files present (dati.py complete)
- [ ] No hardcoded local paths
- [ ] README.md complete and accurate
- [ ] DEPLOY.md up-to-date
- [ ] Requirements.txt includes all dependencies with versions

### Security
- [ ] No API keys in public code
- [ ] Secrets management configured on Streamlit Cloud
- [ ] `.gitignore` prevents accidental commits
- [ ] Repository is public (users need access)
- [ ] No sensitive user data collection

### Git
- [ ] Repository initialized and pushed to GitHub
- [ ] Main branch is clean (no uncommitted changes)
- [ ] Meaningful commit history
- [ ] `.gitignore` is comprehensive
- [ ] All documentation committed

### Performance
- [ ] App loads in under 10 seconds
- [ ] Charts render smoothly
- [ ] No console errors in browser
- [ ] Mobile responsive (test on phone)
- [ ] Handles large datasets efficiently

### Testing
- [ ] Test on Streamlit Cloud staging URL
- [ ] Test on desktop (Chrome, Firefox, Safari)
- [ ] Test on mobile (iOS Safari, Android Chrome)
- [ ] Test all UI interactions
- [ ] Test all calculation scenarios
- [ ] Verify PDF export works (if enabled)
- [ ] Test scenario comparison
- [ ] Test sensitivity analysis

### Post-Deployment
- [ ] Update LinkedIn with launch announcement
- [ ] Share live URL on professional networks
- [ ] Monitor app performance first 24 hours
- [ ] Check error logs for user issues
- [ ] Gather initial user feedback

---

## Post-Launch Monitoring

### Daily (First Week)

- [ ] Check Streamlit Cloud logs for errors
- [ ] Monitor app load times
- [ ] Verify no unexpected crashes
- [ ] Check GitHub for issues/feedback

```bash
# View Streamlit logs (Streamlit Cloud dashboard)
# Settings → Logs
```

### Weekly (Ongoing)

- [ ] Review user feedback (GitHub Issues, LinkedIn DMs)
- [ ] Check performance metrics
- [ ] Verify data freshness
- [ ] Monitor error rates

### Monthly

- [ ] Update property data (if source changes)
- [ ] Update interest rates in dati.py (if rates change significantly)
- [ ] Review and address GitHub issues
- [ ] Deploy any bug fixes or improvements

---

## Updating the App

### Bug Fix Process

1. **Create branch** for fix:
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Make changes** and test locally:
   ```bash
   streamlit run app.py
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Fix: brief description"
   git push origin fix/bug-description
   ```

4. **Create Pull Request** (optional, for code review)

5. **Merge to main**:
   ```bash
   git checkout main
   git merge fix/bug-description
   git push origin main
   ```

6. **Streamlit Cloud auto-deploys** from main branch

### Feature Addition Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement and test**:
   ```bash
   streamlit run app.py
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Feature: add new feature"
   git push origin feature/new-feature
   ```

4. **Merge to main when ready**:
   ```bash
   git checkout main
   git merge feature/new-feature
   git push origin main
   ```

---

## Troubleshooting

### App Won't Deploy on Streamlit Cloud

**Issue**: "Module not found" error

**Solution**: 
- Check `requirements.txt` has all imports
- Verify file paths are relative, not absolute
- Check `.streamlit/config.toml` is valid TOML

**Issue**: Deployment hangs

**Solution**:
- Check requirements.txt for dependencies that take long to install
- Use pinned versions: `streamlit==1.45.0` not `streamlit>=1.0`
- Check Streamlit logs for specific errors

### App Works Locally, Fails on Cloud

**Issue**: Path errors

**Solution**:
```python
# Use relative paths, not absolute
from pathlib import Path
path = Path(__file__).parent / "data.csv"
```

**Issue**: Import errors

**Solution**:
```bash
# Verify all imports work from project root
cd casa-vs-affitto
python -c "from calcoli import ParamsCalcolo; from dati import PROVINCE"
```

### Charts Not Rendering

**Issue**: Plotly charts blank

**Solution**:
- Check browser console for errors
- Verify data is not empty
- Clear Streamlit cache: ⋯ menu → Clear cache

**Issue**: PDF export not working

**Solution**:
- Check browser has JavaScript enabled
- Verify reportlab installed: `pip install reportlab`
- Try different browser

### Performance Issues

**Issue**: App loading slowly

**Solution**:
- Use `@st.cache_data` for expensive computations
- Profile with: `streamlit run app.py --logger.level=debug`
- Check for large file reads

**Issue**: Memory errors

**Solution**:
- Limit data loading to necessary columns
- Use generators instead of loading all data
- Consider pagination for large datasets

---

## Support & Resources

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: [github.com/salvatorederosa/casa-vs-affitto/issues](https://github.com/salvatorederosa/casa-vs-affitto/issues)
- **Email**: salvatore98derosa@gmail.com

---

## Version History

- **v1.0.0** — May 2026 — Initial production deployment

---

Last updated: May 2026
