# Assets Directory

This directory contains media assets for Casa o Affitto.

## screenshot.png

Main application screenshot for social media and promotional materials. Shows:
- App header and title
- Key input controls
- Sample calculation results
- Interactive charts

**Recommended size**: 1200x630px (LinkedIn, Twitter optimal)
**Format**: PNG with transparent background
**Usage**: LinkedIn posts, GitHub README, project portfolio

## linkedin-post.md

Pre-written LinkedIn post copy with multiple versions:
- Main version (professional, comprehensive)
- Casual version (engaging, conversational)
- Technical version (developer-focused)
- Follow-up posts
- Engagement hook posts

Includes:
- Compelling headlines
- Key features
- Demo link
- Hashtags optimized for reach
- Social share copy

## How to Create screenshot.png

1. **Run the app locally**:
   ```bash
   streamlit run app.py
   ```

2. **Take screenshot of desired state**:
   - macOS: Cmd+Shift+4 → Select area
   - Windows: Win+Shift+S
   - Linux: Print Screen

3. **Optimize image**:
   ```bash
   # Install imagemagick if needed
   # macOS: brew install imagemagick
   
   # Resize to 1200x630
   convert screenshot.png -resize 1200x630 screenshot_optimized.png
   
   # Compress
   convert screenshot_optimized.png -quality 85 screenshot.png
   ```

4. **Commit to git**:
   ```bash
   git add assets/screenshot.png
   git commit -m "Add app screenshot for marketing"
   ```

## Sharing Assets

### LinkedIn
- Use screenshot.png as post image
- Use copy from linkedin-post.md
- Include live URL
- Add relevant hashtags

### GitHub README
- Reference screenshot.png in README
- Link to live demo

### Other Channels
- Twitter: Use screenshot + shorter version of post
- Email: Include screenshot + key features
- Portfolio: Include in project showcase section
