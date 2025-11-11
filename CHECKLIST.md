# Activity Recorder - Pre-Launch Checklist

Before distributing Activity Recorder to users, complete this checklist to ensure everything is ready.

## 📋 Development Completion

### Core Functionality
- [x] Native messaging host implementation
- [x] Browser extension (popup, options, background)
- [x] Web dashboard (all pages)
- [x] Landing website
- [x] Documentation (README, guides, etc.)
- [x] Installation scripts

### Testing Required
- [ ] Test native host installation on Windows
- [ ] Test native host installation on macOS
- [ ] Test native host installation on Linux
- [ ] Test browser extension in Chrome
- [ ] Test browser extension in Edge
- [ ] Test browser extension in Brave
- [ ] Test screenshot capture works
- [ ] Test AI analysis works with API key
- [ ] Test activity storage and retrieval
- [ ] Test web dashboard displays activities
- [ ] Test time query feature
- [ ] Test data export
- [ ] Test settings persistence

## 🎨 Assets & Branding

### Icons
- [ ] Create extension icon 16x16
- [ ] Create extension icon 48x48
- [ ] Create extension icon 128x128
- [ ] Create website favicon
- [ ] Create logo.png for README
- [ ] Add to `browser_extension/chrome/icons/`

### Screenshots
- [ ] Take screenshot of extension popup
- [ ] Take screenshot of options page
- [ ] Take screenshot of web dashboard
- [ ] Take screenshot of activities page
- [ ] Take screenshot of time query
- [ ] Add to `website/images/` and `images/README/`

### Demo Content
- [ ] Create demo activity_log.json
- [ ] Create demo screenshots
- [ ] Record demo video (optional)

## 📦 Packaging

### Browser Extension
- [ ] Update manifest.json version
- [ ] Add actual icons to manifest
- [ ] Test extension loads without errors
- [ ] Create extension.zip:
  ```bash
  cd browser_extension/chrome
  zip -r ../../activity-recorder-chrome-v1.0.0.zip . \
    -x "*.git*" -x "README.md" -x "*.DS_Store"
  ```
- [ ] Test installing from ZIP

### Native Host Installers
- [ ] Create Windows installer (.exe):
  ```bash
  pip install pyinstaller
  pyinstaller --onefile --name activity-recorder-native-host native_host.py
  ```
- [ ] Create macOS installer (.dmg or .pkg)
- [ ] Create Linux AppImage or .deb package
- [ ] Add installers to `website/downloads/`
- [ ] Test each installer on respective platform

### Web Dashboard
- [ ] Build production version:
  ```bash
  cd web_dashboard
  npm run build
  ```
- [ ] Test production build works
- [ ] Create deployment ZIP (optional):
  ```bash
  cd dist
  zip -r ../../activity-recorder-dashboard-v1.0.0.zip .
  ```

## 🌐 Website Setup

### Landing Page
- [ ] Add actual screenshots
- [ ] Update download links
- [ ] Add GitHub repository URL
- [ ] Test all links work
- [ ] Test responsive design on mobile
- [ ] Optimize images
- [ ] Add Google Analytics (optional)

### Hosting
- [ ] Choose hosting provider (GitHub Pages, Netlify, etc.)
- [ ] Set up domain (optional)
- [ ] Deploy website
- [ ] Test deployed site
- [ ] Set up SSL certificate

## 📚 Documentation

### Update URLs
- [ ] Replace `yourusername` with actual GitHub username in:
  - [ ] README.md
  - [ ] GETTING_STARTED.md
  - [ ] MIGRATION_GUIDE.md
  - [ ] website/index.html
  - [ ] All other docs
- [ ] Update all `github.com/yourusername/activity-recorder` links
- [ ] Add actual website URL if available

### Verify Content
- [ ] README.md is accurate
- [ ] GETTING_STARTED.md tested by fresh user
- [ ] MIGRATION_GUIDE.md reviewed
- [ ] All code examples work
- [ ] All screenshots current
- [ ] All links valid

### Add Missing Docs
- [ ] Create LICENSE file (if not exists)
- [ ] Create CHANGELOG.md
- [ ] Create CONTRIBUTING.md
- [ ] Create CODE_OF_CONDUCT.md (optional)
- [ ] Add API documentation (if needed)

## 🔐 Security & Privacy

### Code Review
- [ ] No hardcoded API keys
- [ ] No sensitive data in repository
- [ ] Proper error handling everywhere
- [ ] Input validation on user inputs
- [ ] Secure API key storage (Chrome storage API)

### Privacy Policy
- [ ] Create privacy.html for website
- [ ] Explain data collection (local only)
- [ ] Explain API usage (DashScope)
- [ ] Add to Chrome Web Store listing

### Terms of Service
- [ ] Create terms.html (optional)
- [ ] Disclaimer about screenshot content
- [ ] Usage guidelines

## 🚀 Distribution

### GitHub Repository
- [ ] Create public repository
- [ ] Push all code
- [ ] Create GitHub releases
- [ ] Tag v1.0.0
- [ ] Add release notes
- [ ] Set up GitHub Issues
- [ ] Set up GitHub Discussions
- [ ] Add topics/tags

### Chrome Web Store
- [ ] Create developer account ($5 fee)
- [ ] Prepare store listing:
  - [ ] Name: "Activity Recorder"
  - [ ] Short description (132 chars max)
  - [ ] Detailed description
  - [ ] Category: Productivity
  - [ ] Screenshots (1280x800 or 640x400)
  - [ ] Promotional images (if needed)
  - [ ] Privacy policy URL
  - [ ] Support URL (GitHub Issues)
- [ ] Upload extension ZIP
- [ ] Submit for review
- [ ] Wait for approval (1-3 days)
- [ ] Update website with store link

### NPM Package (Optional)
- [ ] Publish web dashboard as npm package
- [ ] Add installation instructions

### PyPI Package (Optional)
- [ ] Package native host for PyPI
- [ ] Add installation instructions

## 📣 Marketing & Community

### Launch Announcement
- [ ] Write launch blog post
- [ ] Post on Reddit (r/productivity, r/Chrome, etc.)
- [ ] Post on Hacker News
- [ ] Tweet announcement
- [ ] Post on Product Hunt
- [ ] Share in relevant Discord servers
- [ ] Email beta testers (if any)

### Social Media
- [ ] Create Twitter account (optional)
- [ ] Create project hashtag
- [ ] Prepare demo GIFs/videos
- [ ] Engage with early users

### Community Setup
- [ ] Set up Discord server (optional)
- [ ] Monitor GitHub Issues daily
- [ ] Respond to feedback
- [ ] Plan regular updates

## 🔧 Post-Launch

### Monitoring
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor Chrome Web Store reviews
- [ ] Monitor GitHub Issues
- [ ] Track download statistics
- [ ] Collect user feedback

### Support
- [ ] Create FAQ from common questions
- [ ] Update troubleshooting guide
- [ ] Respond to issues within 24-48 hours
- [ ] Create video tutorials (if needed)

### Iteration
- [ ] Plan v1.1 features based on feedback
- [ ] Fix critical bugs immediately
- [ ] Release patches as needed
- [ ] Update documentation

## ✅ Pre-Launch Final Check

Before going live, verify:

### Installation Flow
- [ ] Fresh Windows install works
- [ ] Fresh macOS install works
- [ ] Fresh Linux install works
- [ ] All steps in GETTING_STARTED.md work
- [ ] Extension connects to native host
- [ ] First screenshot captures successfully
- [ ] AI analysis returns results
- [ ] Data saves correctly

### User Experience
- [ ] Extension popup loads quickly
- [ ] Options page saves settings
- [ ] Dashboard loads activities
- [ ] Time query works
- [ ] Export works
- [ ] Error messages are helpful
- [ ] No confusing UI elements

### Documentation
- [ ] README makes sense to newcomers
- [ ] Installation guide is clear
- [ ] Troubleshooting covers common issues
- [ ] All screenshots are current
- [ ] All links work

### Legal
- [ ] License file present
- [ ] Copyright notices correct
- [ ] Privacy policy complete
- [ ] No licensing issues with dependencies

## 🎯 Success Metrics

Define success criteria:
- [ ] Download/install goal (e.g., 100 users in first month)
- [ ] User retention rate target
- [ ] Average rating target (4+ stars)
- [ ] Active development commitment (weekly updates)

## 📅 Launch Timeline

Create your launch plan:

**Week 1: Pre-Launch**
- Complete checklist items
- Internal testing
- Beta testing with small group

**Week 2: Soft Launch**
- GitHub repository public
- Chrome Web Store submission
- Limited social media announcement

**Week 3: Full Launch**
- Chrome Web Store approved
- Full marketing push
- Product Hunt launch
- Reddit/HN posts

**Week 4: Post-Launch**
- Bug fixes
- User support
- Collect feedback
- Plan v1.1

## 📝 Notes

Use this space for notes, blockers, or items needing discussion:

```
# Notes:
-
-
-

# Blockers:
-
-

# Questions:
-
-
```

---

**Last Updated**: [Date]
**Completed**: 0/100+ items
**Status**: 🚧 Pre-Launch Preparation

**Next Action**: Start with "Testing Required" section
