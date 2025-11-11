# Getting Started with Activity Recorder

A quick-start guide to get Activity Recorder up and running in 10 minutes.

## 📋 What You Need

Before starting, make sure you have:

- [ ] **Python 3.8 or higher** installed ([Download Python](https://www.python.org/downloads/))
- [ ] **Chrome, Edge, Brave, or another Chromium browser**
- [ ] **DashScope API Key** ([Get free key](https://dashscope.aliyun.com/))
- [ ] **10 minutes** of your time

## 🚀 Quick Install (3 Steps)

### Step 1: Install Python Backend (2 minutes)

Open your terminal and run:

```bash
# Clone or download the project
cd auto_record_my_activates

# Install dependencies
pip install -r requirements.txt
```

<details>
<summary>💡 Using uv instead of pip?</summary>

```bash
uv pip install -r requirements.txt
```
</details>

<details>
<summary>⚠️ Getting permission errors?</summary>

Try using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
</details>

### Step 2: Install Native Host (1 minute)

The native host enables the browser extension to capture screenshots:

```bash
cd browser_extension/native_host
python install.py
```

You should see: `✓ Native messaging host installed successfully!`

<details>
<summary>❌ Installation failed?</summary>

**Windows**: Run Command Prompt as Administrator
**macOS/Linux**: Check Python 3 is installed: `python3 --version`
**All**: Verify the manifest file was created in the correct location (installer shows the path)
</details>

### Step 3: Install Browser Extension (2 minutes)

1. Open Chrome and go to **chrome://extensions/**
2. Enable **"Developer mode"** (toggle switch in top right corner)
3. Click **"Load unpacked"** button
4. Navigate to and select: `auto_record_my_activates/browser_extension/chrome/`
5. The Activity Recorder extension appears in your toolbar! 🎉

**Important**: Copy the **Extension ID** (looks like: `abcdefghijklmnopqrstuvwxyz123456`)

### Step 3.5: Link Extension to Native Host (1 minute)

1. Open `browser_extension/native_host/com.activity_recorder.host.json` in a text editor
2. Find the line: `"chrome-extension://EXTENSION_ID_WILL_BE_REPLACED/"`
3. Replace `EXTENSION_ID_WILL_BE_REPLACED` with your actual Extension ID
4. Save the file
5. Run the installer again:
   ```bash
   cd browser_extension/native_host
   python install.py
   ```

## ⚙️ Configure API Key (2 minutes)

1. Get your **free** DashScope API key:
   - Go to [dashscope.aliyun.com](https://dashscope.aliyun.com/)
   - Sign up (free tier includes 1M tokens/month)
   - Navigate to **API Keys** section
   - Click **Create Key**
   - Copy your API key (starts with `sk-`)

2. Add API key to the extension:
   - Click the **Activity Recorder** icon in your browser toolbar
   - Click **"Settings"** in the popup
   - Paste your API key in the **"DashScope API Key"** field
   - Click **"Save Settings"**

## 🎬 Start Recording (1 minute)

You're ready! Let's test it:

1. Click the **Activity Recorder** extension icon
2. Click **"Start Recording"**
3. Wait 3 minutes (or click **"Capture Now"** for immediate test)
4. View your first activity in the popup!

**Congratulations! 🎉 You've successfully set up Activity Recorder!**

## 📊 Optional: Web Dashboard (5 minutes)

For a better viewing experience, set up the web dashboard:

```bash
cd web_dashboard
npm install
npm run dev
```

Open **http://localhost:3000** in your browser to view your activities.

<details>
<summary>Don't have Node.js?</summary>

Download from [nodejs.org](https://nodejs.org/) (choose LTS version)
</details>

## ✅ Verify Everything Works

Let's make sure everything is set up correctly:

### Test 1: Extension Can Connect to Native Host

1. Click extension icon
2. Look for the **status indicator** - should show "Stopped" (not "Not Connected")
3. ✅ If it says "Stopped" or "Recording" → Success!
4. ❌ If it says "Cannot connect to native host" → See [Troubleshooting](#troubleshooting) below

### Test 2: Screenshot Capture Works

1. Click **"Start Recording"**
2. Immediately click **"Capture Now"** (don't wait 3 minutes)
3. You should see a notification: "Capture successful"
4. Check if `screenshots/` directory has a new PNG file
5. ✅ New screenshot file exists → Success!

### Test 3: AI Analysis Works

1. After capturing, check the extension popup
2. Under "Recent Activities", you should see your first activity
3. Description should be in English or Chinese (depending on prompt)
4. ✅ Activity has meaningful description → Success!

### Test 4: Data is Saved

1. Open `activity_log.json` in a text editor
2. You should see a JSON object with an "activities" array
3. Your test activity should be listed
4. ✅ Activity in JSON file → Success!

## 🎛️ Customize Your Setup

### Change Screenshot Interval

**Default**: 3 minutes (180 seconds)

To change:
1. Click extension icon → Settings
2. Change **"Capture Interval"**
3. Click **"Save Settings"**

**Recommendations**:
- **Frequent tracking**: 1-2 minutes (uses more API calls)
- **Normal use**: 3-5 minutes (recommended)
- **Light tracking**: 10-15 minutes (saves API costs)

### Enable Auto-Start

Make recording start automatically when you launch your browser:

1. Extension Settings
2. Enable **"Auto-start Recording"**
3. Save

### Choose AI Model

**Default**: qwen3-vl-plus (best balance of speed & accuracy)

Other options:
- **qwen3-vl-max**: Higher accuracy, slower, more expensive
- **qwen-vl-plus**: Older model, faster, cheaper

Change in Extension Settings → AI Model dropdown

### Adjust Data Retention

**Default**: Keep 30 days of activities, 50 screenshots

Change in Extension Settings:
- **Data Retention**: Days to keep activity records
- **Max Screenshots**: Number of screenshots to keep

## 📱 Daily Usage Tips

### Starting Your Day

1. Open browser (auto-start if enabled)
2. Or click extension → **"Start Recording"**
3. Go about your day normally

### During the Day

- Extension runs in background
- Screenshots captured automatically
- No action needed!

### Reviewing Your Activities

**Quick View**:
- Click extension icon
- See recent activities in popup

**Detailed View**:
- Click **"View Dashboard"**
- Browse all activities
- Use search and filters

### Querying Your Time

Want to know what you did in the last few hours?

1. Open web dashboard (or use extension popup)
2. Go to **"Time Query"** page
3. Select time range or choose quick option:
   - Last 1 hour
   - Last 3 hours
   - Today
   - Custom range
4. Click **"Query Activities"**
5. Get AI-powered summary!

### End of Day

- Recording continues until you stop it
- Or will auto-stop when you close browser
- Data is automatically saved

## 🔧 Troubleshooting

### "Cannot connect to native host"

**This is the most common issue. Try these in order:**

1. **Verify native host is installed**:
   ```bash
   cd browser_extension/native_host
   python install.py
   ```

2. **Check extension ID matches**:
   - Open `chrome://extensions/`
   - Copy Extension ID
   - Open `browser_extension/native_host/com.activity_recorder.host.json`
   - Verify ID matches in `allowed_origins`
   - If not, update and re-run installer

3. **Test native host directly**:
   ```bash
   cd auto_record_my_activates
   echo '{"command":"get_status"}' | python native_host.py
   ```
   Should return JSON with status. If error, check Python dependencies.

4. **Check logs**:
   ```bash
   cat browser_extension/native_host/native_host_error.log
   ```

5. **Restart browser** after fixing issues

### "API key error" or "Analysis failed"

1. **Verify API key is correct**:
   - Log in to [DashScope Console](https://dashscope.console.aliyun.com/)
   - Check your API key
   - Ensure it's active and has quota

2. **Re-enter API key**:
   - Extension Settings
   - Delete and re-paste API key
   - Save

3. **Check network**:
   - Ensure you have internet connection
   - DashScope API requires internet access

### Screenshots are blank or black

**Windows**:
- Check if another app is blocking screen capture
- Try running with administrator privileges

**macOS**:
- System Preferences → Security & Privacy → Screen Recording
- Enable permission for Chrome and Terminal

**Linux**:
- Verify `$DISPLAY` is set: `echo $DISPLAY`
- Install dependencies: `sudo apt-get install python3-xlib` (if needed)

### Web dashboard shows no activities

1. **Check activity_log.json exists**:
   ```bash
   ls -l activity_log.json
   ```

2. **For development, copy to public/**:
   ```bash
   cp activity_log.json web_dashboard/public/
   cp -r screenshots/ web_dashboard/public/
   ```

3. **Check browser console** (F12) for errors

### Extension disappeared from toolbar

1. Go to **chrome://extensions/**
2. Verify "Activity Recorder" is enabled
3. Click the **puzzle piece icon** in toolbar
4. **Pin** Activity Recorder to toolbar

## 🆘 Still Having Issues?

If you're still stuck after trying the troubleshooting steps:

1. **Check the logs**:
   - Native host: `browser_extension/native_host/native_host_error.log`
   - Python: `activity_recorder.log`
   - Extension: chrome://extensions/ → Service Worker → Console

2. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/activity-recorder/issues)

3. **Ask for help**: [GitHub Discussions](https://github.com/yourusername/activity-recorder/discussions)

4. **Report a bug**: [New Issue](https://github.com/yourusername/activity-recorder/issues/new)

Include in your report:
- Operating system
- Python version (`python --version`)
- Browser and version
- Relevant error messages from logs
- Steps to reproduce

## 📚 Next Steps

Now that you're set up, explore these guides:

- **[User Guide](browser_extension/chrome/README.md)**: Detailed feature documentation
- **[Migration Guide](MIGRATION_GUIDE.md)**: If upgrading from PyQt app
- **[FAQ](website/index.html#faq)**: Common questions
- **[API Reference](native_host.py)**: For developers

## 🎉 You're All Set!

Activity Recorder is now running and tracking your activities. Here are some things to try:

- [ ] Review your first day of activities
- [ ] Try the time query feature
- [ ] Customize your recording interval
- [ ] Set up auto-start for convenience
- [ ] Export your data
- [ ] Explore the web dashboard

**Happy tracking! 📊**
