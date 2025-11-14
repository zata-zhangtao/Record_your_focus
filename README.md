# Activity Recorder - AI-Powered Activity Tracking

<div align="center">

![Logo](logo.png)

**Automatically capture and analyze your computer activities with AI-powered insights**

[Features](#features) • [Download](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## 🎯 Overview

Activity Recorder is an intelligent activity tracking system that automatically captures screenshots and uses AI to understand what you're doing. Perfect for productivity tracking, time management, and understanding your work patterns.

### 🆕 New Browser-Based Architecture

We've completely migrated from a PyQt desktop application to a modern **browser extension + native host** architecture, offering:

- 🌐 **Browser Integration**: Control everything from your browser toolbar
- 🖥️ **Full Desktop Capture**: Capture entire desktop screen, not just browser windows
- 📊 **Web Dashboard**: Modern React-based interface for viewing activities
- 🔒 **Privacy-First**: All data stays on your computer
- 🚀 **Cross-Platform**: Works on Windows, macOS, and Linux

---

## ✨ Features

### Core Capabilities

- 🔄 **Automatic Screenshots**: Captures desktop every 1-60 minutes (customizable)
- 🤖 **AI Analysis**: Qwen-VL vision models analyze screenshots with 95%+ accuracy
- 📝 **Activity Timeline**: Browse, search, and filter your complete activity history
- ⏰ **Time Query**: Ask AI "What did I do in the last 3 hours?" with one-tap hourly presets (09–24) on both the web dashboard and legacy PyQt UI
- 📊 **Statistics**: Track productivity, success rates, and activity patterns
- 💾 **Data Export**: Export activities as JSON for external analysis
- 🔐 **Privacy**: All data stored locally, you control everything

### Technical Features

- **Native Messaging**: Browser extension communicates with Python backend
- **Cross-Browser**: Chrome, Edge, Brave, and all Chromium-based browsers
- **Modern UI**: React-based web dashboard with responsive design
- **Async Processing**: Non-blocking workflow using asyncio and LangGraph
- **Smart Cleanup**: Automatic retention policies for screenshots and activities

---

## 📦 Quick Start

### Prerequisites

1. **Python 3.8+** with pip or uv
2. **DashScope API Key** from [Alibaba Cloud](https://dashscope.aliyun.com/) (free tier available)
3. **Chromium-based browser** (Chrome, Edge, Brave, etc.)

### Installation (3 Steps)

#### 1️⃣ Install Python Dependencies

```bash
cd auto_record_my_activates
pip install -r requirements.txt
# or with uv
uv pip install -r requirements.txt
```

#### 2️⃣ Install Native Messaging Host

```bash
cd browser_extension/native_host
python install.py
```

This registers the native host so the browser extension can communicate with Python.

#### 3️⃣ Install Browser Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select `browser_extension/chrome/` directory
5. Copy the **Extension ID** from the card
6. Edit `browser_extension/native_host/com.activity_recorder.host.json`
7. Replace `EXTENSION_ID_WILL_BE_REPLACED` with your actual extension ID
8. Run `python install.py` again to update the manifest

#### 4️⃣ Configure API Key

1. Click the extension icon in your browser toolbar
2. Click "Settings"
3. Enter your DashScope API key
4. Save settings

### 🎉 Start Recording!

Click the extension icon and hit "Start Recording". Screenshots will be captured automatically and analyzed by AI.

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser Extension                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Popup UI  │  │   Settings   │  │  Background SW   │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ Native Messaging Protocol
                             │ (JSON via stdin/stdout)
┌────────────────────────────▼────────────────────────────────┐
│                    Native Host (Python)                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Screenshot │→ │ AI Analysis │→ │ Storage (JSON/Files) │ │
│  │  (mss lib) │  │  (Qwen-VL)  │  │                      │ │
│  └────────────┘  └─────────────┘  └──────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │ Read Data
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Web Dashboard (React)                   │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────────┐ │
│  │ Dashboard  │  │ Activities │  │     Time Query        │ │
│  └────────────┘  └────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Scheduling**: Browser extension's background service worker schedules captures using `chrome.alarms`
2. **Trigger**: At interval, extension sends `capture_now` command to native host
3. **Capture**: Native host uses `mss` library to capture full desktop screenshot
4. **Analysis**: Screenshot sent to DashScope API (Qwen-VL model) with base64 encoding
5. **Storage**: Activity description and metadata saved to `activity_log.json`
6. **Display**: Web dashboard reads JSON file and displays activities

---

## 📁 Project Structure

```
auto_record_my_activates/
├── 📦 Core Python Backend
│   ├── native_host.py           # Native messaging host
│   ├── workflow.py               # LangGraph workflow
│   ├── screenshot_agent.py       # Screenshot capture (mss)
│   ├── analysis_agent.py         # AI analysis (DashScope)
│   ├── storage.py                # JSON storage
│   └── config.py                 # Configuration
│
├── 🌐 Browser Extension
│   └── browser_extension/
│       ├── chrome/               # Chrome extension (Manifest V3)
│       │   ├── manifest.json
│       │   ├── background.js     # Service worker
│       │   ├── popup.html/css/js # Extension popup
│       │   ├── options.html/css/js # Settings page
│       │   └── icons/
│       └── native_host/          # Native host installer
│           ├── install.py
│           ├── com.activity_recorder.host.json
│           └── native_host_launcher.sh/.bat
│
├── 🎨 Web Dashboard
│   └── web_dashboard/
│       ├── src/
│       │   ├── components/       # React components
│       │   ├── pages/            # Dashboard, Activities, TimeQuery, Settings
│       │   └── App.jsx
│       ├── package.json
│       └── vite.config.js
│
├── 🌍 Landing Website
│   └── website/
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── 🖥️ Legacy PyQt GUI (Deprecated)
│   ├── main_gui.py
│   └── gui/
│
├── 📊 Data & Assets
│   ├── activity_log.json         # Activity records
│   ├── screenshots/              # Screenshot storage
│   └── logo.png
│
└── 📚 Documentation
    ├── README.md                  # This file
    └── requirements.txt
```

---

## 📖 Documentation

### For Users

- **[Installation Guide](browser_extension/chrome/README.md)**: Detailed setup instructions
- **[Native Host Setup](browser_extension/native_host/README.md)**: Native messaging configuration
- **[Web Dashboard Guide](web_dashboard/README.md)**: Using the web interface
- **[Website](website/index.html)**: Landing page with downloads and FAQ

### For Developers

- **Native Messaging Protocol**: See `native_host.py` for command reference
- **Extension API**: See `browser_extension/chrome/background.js` for message handling
- **Data Format**: Activities stored in JSON format (see below)

### Configuration

#### Extension Settings (via options page)

```javascript
{
  interval: 180,          // Screenshot interval in seconds
  autoStart: false,       // Auto-start on browser launch
  apiKey: "sk-xxx",      // DashScope API key
  modelName: "qwen3-vl-plus",  // AI model
  thinkingMode: true,    // Enable AI thinking mode
  retentionDays: 30,     // Data retention period
  maxScreenshots: 50     // Max screenshots to keep
}
```

#### Native Host Configuration (`config.py`)

```python
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
MODEL_NAME = "qwen3-vl-plus"
SCREENSHOT_INTERVAL = 180  # seconds
SCREENSHOT_DIR = "screenshots"
ACTIVITY_LOG_FILE = "activity_log.json"
```

---

## 💾 Data Format

### Activity Record Structure

```json
{
  "created_at": "2025-01-11T10:00:00",
  "activities": [
    {
      "timestamp": "2025-01-11T10:03:00.123456",
      "screenshot_path": "screenshots/screenshot_20250111_100300.png",
      "activity_description": "User is coding in VS Code, working on a Python project",
      "analysis_result": {
        "activity_description": "User is coding in VS Code, working on a Python project",
        "confidence": "high",
        "analysis_successful": true,
        "error": null
      },
      "confidence": "high",
      "analysis_successful": true,
      "error": null
    }
  ]
}
```

### Screenshot Storage

- **Location**: `screenshots/` directory
- **Format**: PNG (lossless)
- **Naming**: `screenshot_YYYYMMDD_HHMMSS.png`
- **Cleanup**: Automatic (keeps last 50 by default)

---

## 🔧 Advanced Usage

### Native Messaging Commands

The browser extension can send these commands to the native host:

```javascript
// Start automatic recording
{
  "command": "start_recording",
  "interval": 180  // seconds
}

// Stop recording
{
  "command": "stop_recording"
}

// Immediate capture
{
  "command": "capture_now"
}

// Get activities
{
  "command": "get_activities",
  "limit": 10,
  "date": "2025-01-11"  // optional
}

// Time range query
{
  "command": "query_time_range",
  "start_time": "2025-01-11T09:00:00",
  "end_time": "2025-01-11T12:00:00",
  "query": "总结这段时间的活动"
}

// Get status
{
  "command": "get_status"
}

// Update settings
{
  "command": "update_settings",
  "settings": {
    "interval": 300,
    "api_key": "sk-xxx",
    "model_name": "qwen3-vl-max"
  }
}
```

### Running Web Dashboard

```bash
cd web_dashboard
npm install
npm run dev  # Development server on http://localhost:3000

# Production build
npm run build
npm run preview
```

### Direct Python Usage (Legacy)

You can still run the native host directly for testing:

```bash
# Continuous recording (CLI)
python workflow.py

# Or use the legacy GUI
python main_gui.py
```

---

## 🚀 Deployment

### Browser Extension

#### Chrome Web Store (Recommended)

1. Prepare package: `cd browser_extension/chrome && zip -r extension.zip .`
2. Create Chrome Web Store developer account ($5 one-time)
3. Upload ZIP and fill in metadata
4. Submit for review (1-3 days)
5. Update `allowed_origins` in native host manifest with published extension ID

#### Manual Installation (Development)

Users can install unpacked extension from `browser_extension/chrome/` directory.

### Native Host

Create installers for each platform:

#### Windows

```bash
pip install pyinstaller
pyinstaller --onefile native_host.py
# Creates dist/native_host.exe
```

#### macOS

```bash
pyinstaller --onefile --windowed native_host.py
# Create .app bundle or .dmg
```

#### Linux

```bash
pip install pyinstaller
pyinstaller --onefile native_host.py
# Or create .deb/.rpm package
```

### Web Dashboard

#### Static Hosting

```bash
cd web_dashboard
npm run build
# Deploy dist/ to Netlify, Vercel, GitHub Pages, etc.
```

#### Local Server

```bash
npm run preview  # Vite preview server
# Or use nginx, Apache, etc.
```

---

## 🛠️ Troubleshooting

### Extension Can't Connect to Native Host

**Symptoms**: "Cannot connect to native host" error in extension popup

**Solutions**:
1. Verify native host is installed: `python browser_extension/native_host/install.py`
2. Check manifest exists:
   - **Linux**: `~/.config/google-chrome/NativeMessagingHosts/com.activity_recorder.host.json`
   - **macOS**: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`
   - **Windows**: `%APPDATA%\Google\Chrome\NativeMessagingHosts\`
3. Verify extension ID matches in manifest's `allowed_origins`
4. Check logs: `browser_extension/native_host/native_host_error.log`
5. Test native host: `echo '{"command":"get_status"}' | python native_host.py`

### Screenshots Not Capturing

**Solutions**:
1. Verify Python dependencies: `pip install -r requirements.txt`
2. Check `mss` library works: `python -c "from mss import mss; mss().shot()"`
3. Linux: Verify `$DISPLAY` is set: `echo $DISPLAY`
4. Check permissions (screen recording on macOS)
5. View native host logs

### AI Analysis Failing

**Solutions**:
1. Verify API key is valid at [DashScope Console](https://dashscope.console.aliyun.com/)
2. Check API key has access to vision models (qwen3-vl-plus)
3. Test API directly:
   ```python
   import dashscope
   dashscope.api_key = "your-key"
   # Test call
   ```
4. Check network connectivity
5. Review error logs: `activity_recorder.log`

### Dashboard Not Loading Activities

**Solutions**:
1. Verify `activity_log.json` exists in project root
2. Check file permissions
3. For development: Copy/symlink JSON to `web_dashboard/public/`
4. Check browser console for fetch errors
5. Ensure dashboard can access screenshot files

### Extension Not Auto-Starting

**Solutions**:
1. Enable "Auto-start Recording" in extension options
2. Reload extension after setting change
3. Check browser is allowed to run on startup
4. Verify no errors in background service worker console

---

## 🔐 Privacy & Security

### Data Storage

- **Location**: All data stored locally on your computer
- **Screenshots**: `screenshots/` directory (PNG files)
- **Activities**: `activity_log.json` (text file)
- **No Cloud**: No data sent to external servers except DashScope API

### API Communication

- **DashScope API**: Only endpoint receiving data (for AI analysis)
- **Your API Key**: You own and control the API key
- **Data Transmission**: Screenshots sent as base64 to DashScope only
- **HTTPS**: All API calls use encrypted HTTPS

### Data Control

- **Retention**: Configure automatic cleanup (default: 30 days activities, 50 screenshots)
- **Export**: Export all data as JSON anytime
- **Deletion**: Delete individual activities or clear all data
- **Pause**: Stop recording anytime

### Recommendations

- 🔐 Keep API key secure (don't share)
- 📅 Set reasonable retention policies
- 🗑️ Regularly review and clean old data
- ⏸️ Pause recording when working with sensitive information
- 🔍 Review screenshots before sharing exported data

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

- Use [GitHub Issues](https://github.com/yourusername/activity-recorder/issues)
- Include logs, screenshots, and steps to reproduce
- Check existing issues first

### Submitting Pull Requests

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/activity-recorder.git
cd activity-recorder

# Install Python dependencies
pip install -r requirements.txt

# Install native host
cd browser_extension/native_host && python install.py

# Load extension in Chrome (chrome://extensions/)

# Start dashboard development server
cd web_dashboard && npm install && npm run dev
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **DashScope API**: Alibaba Cloud for Qwen-VL vision models
- **mss**: Fast cross-platform screenshot library
- **LangGraph**: Workflow orchestration framework
- **React**: Modern UI framework
- **PyQt6**: Legacy GUI framework (deprecated)

---

## 📮 Contact & Support

- **GitHub**: [yourusername/activity-recorder](https://github.com/yourusername/activity-recorder)
- **Issues**: [Report a bug](https://github.com/yourusername/activity-recorder/issues)
- **Discussions**: [Ask questions](https://github.com/yourusername/activity-recorder/discussions)
- **Website**: [activity-recorder.com](https://activity-recorder.com) (if deployed)

---

## 🗺️ Roadmap

### ✅ Completed

- [x] PyQt desktop application
- [x] Browser extension (Chrome)
- [x] Native messaging host
- [x] Web dashboard (React)
- [x] AI analysis (Qwen-VL)
- [x] Activity timeline
- [x] Time query feature
- [x] Data export

### 🚧 In Progress

- [ ] Chrome Web Store publication
- [ ] Safari extension
- [ ] Installer packages (Windows/macOS/Linux)

### 📋 Planned

- [ ] Firefox extension
- [ ] Advanced filtering and search
- [ ] Custom AI prompts/templates
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Activity categories/tags
- [ ] Productivity insights and reports
- [ ] Cloud sync (optional)
- [ ] Mobile companion app
- [ ] Team/organization features

### 💡 Ideas

- Application-specific filtering
- Smart notifications
- Integration with time tracking tools
- Export to various formats (CSV, PDF)
- Customizable dashboard widgets
- Voice notes annotation
- Activity reminders

---

<div align="center">

**Made with ❤️ by the Activity Recorder Team**

[⬆ Back to Top](#activity-recorder---ai-powered-activity-tracking)

</div>
