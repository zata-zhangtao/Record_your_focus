# Activity Recorder - Chrome Extension

A browser extension for automatically recording and analyzing your computer activities using AI.

## Features

- 🎯 **Automatic Screenshot Capture**: Periodic desktop screenshots at customizable intervals
- 🤖 **AI-Powered Analysis**: Qwen-VL models analyze screenshots to understand your activities
- 📊 **Activity Timeline**: View and search through your activity history
- ⚙️ **Flexible Configuration**: Customize capture intervals, AI models, and data retention
- 🔒 **Privacy First**: All processing done locally with your own API key

## Prerequisites

1. **Native Messaging Host**: This extension requires the native messaging host to be installed
   - Follow the installation guide in `browser_extension/native_host/README.md`
   - The native host enables desktop screenshot capture capabilities

2. **DashScope API Key**: Get a free API key from [Alibaba Cloud DashScope](https://dashscope.aliyun.com/)
   - Supports Qwen-VL vision models for activity analysis

3. **Python Dependencies**: The native host requires Python 3.8+ with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Installation

### Step 1: Install Native Messaging Host

```bash
# Navigate to the native host directory
cd browser_extension/native_host

# Run the installer
python3 install.py
```

### Step 2: Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `browser_extension/chrome` directory
5. Copy the **Extension ID** from the extension card

### Step 3: Update Native Host Manifest

1. Open `browser_extension/native_host/com.activity_recorder.host.json`
2. Replace `EXTENSION_ID_WILL_BE_REPLACED` with your actual extension ID
3. Re-run the installer: `python3 install.py`

### Step 4: Configure API Key

1. Click the extension icon in Chrome toolbar
2. Click "Settings" to open the options page
3. Enter your DashScope API key
4. Save settings

## Usage

### Basic Operation

1. **Start Recording**:
   - Click the extension icon
   - Click "Start Recording"
   - Screenshots will be captured at the configured interval (default: 3 minutes)

2. **Manual Capture**:
   - Click "Capture Now" to take an immediate screenshot

3. **View Activities**:
   - Click "View Dashboard" to see your activity timeline
   - (Dashboard must be running separately - see Web Dashboard section)

4. **Settings**:
   - Click "Settings" to configure:
     - Capture interval
     - Auto-start recording
     - AI model selection
     - Data retention policies

### Extension Popup

The popup provides quick access to:
- **Status Indicator**: Shows if recording is active
- **Start/Stop Recording**: Toggle automatic capture
- **Capture Now**: Manual screenshot trigger
- **Interval Settings**: Quick interval adjustment
- **Statistics**: Total activities and success rate

### Options Page

Access full settings via:
- Click "Settings" in popup
- Right-click extension icon → "Options"
- Visit `chrome://extensions/?options=<extension_id>`

Configure:
- **Recording Settings**: Interval, auto-start
- **API Configuration**: API key, model selection, thinking mode
- **Data Management**: Retention period, export data

## File Structure

```
chrome/
├── manifest.json          # Extension manifest (Manifest V3)
├── background.js          # Service worker (native messaging, scheduling)
├── popup.html/css/js      # Extension popup UI
├── options.html/css/js    # Settings page
├── icons/                 # Extension icons (16x16, 48x48, 128x128)
└── README.md             # This file
```

## Native Messaging Protocol

The extension communicates with the native host using Chrome's native messaging protocol:

### Commands

- `start_recording`: Start automatic capture
- `stop_recording`: Stop automatic capture
- `capture_now`: Trigger immediate capture
- `get_activities`: Fetch activity records
- `get_status`: Get current status
- `update_settings`: Update configuration
- `get_statistics`: Get activity statistics

### Example Message

```javascript
// Send to native host
{
  "command": "start_recording",
  "interval": 180  // seconds
}

// Response from native host
{
  "command": "start_recording",
  "success": true,
  "interval": 180,
  "message": "Recording started"
}
```

## Troubleshooting

### Extension can't connect to native host

**Symptoms**: "Cannot connect to native host" message in popup

**Solutions**:
1. Verify native host is installed: `python3 browser_extension/native_host/install.py`
2. Check manifest file exists:
   - Linux: `~/.config/google-chrome/NativeMessagingHosts/com.activity_recorder.host.json`
   - macOS: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.activity_recorder.host.json`
   - Windows: `%APPDATA%\Google\Chrome\NativeMessagingHosts\com.activity_recorder.host.json`
3. Verify extension ID in manifest matches installed extension
4. Check native host logs: `browser_extension/native_host/native_host_error.log`

### Screenshots not capturing

**Solutions**:
1. Verify Python dependencies are installed: `pip install -r requirements.txt`
2. Check native host has permission to capture screen
3. View native host logs for errors
4. Test native host directly: `python3 native_host.py` (then send JSON commands)

### API key not working

**Solutions**:
1. Verify API key is valid at [DashScope Console](https://dashscope.console.aliyun.com/)
2. Check API key has access to vision models (qwen3-vl-plus)
3. Ensure API key is saved in extension settings
4. Check native host receives API key (view logs)

### Recording not starting automatically

**Solutions**:
1. Enable "Auto-start Recording" in extension settings
2. Reload extension after enabling auto-start
3. Check browser is allowed to run on startup

## Development

### Testing the Extension

1. Make changes to extension files
2. Go to `chrome://extensions/`
3. Click the reload icon on the extension card
4. Test functionality in popup/options page

### Debugging

1. **Background Service Worker**:
   - Go to `chrome://extensions/`
   - Click "Service worker" link under extension
   - View console logs

2. **Popup/Options**:
   - Right-click popup/options page
   - Select "Inspect"
   - View console in DevTools

3. **Native Host**:
   - Check `browser_extension/native_host/native_host.log`
   - Check `browser_extension/native_host/native_host_error.log`

### Building for Production

1. Update version in `manifest.json`
2. Create icons: Generate 16x16, 48x48, 128x128 PNG icons
3. Test all features
4. Create ZIP package:
   ```bash
   cd browser_extension/chrome
   zip -r activity-recorder-chrome.zip . -x "*.git*" -x "README.md"
   ```
5. Upload to Chrome Web Store

## Privacy & Security

- All screenshot processing happens locally on your machine
- API key is stored in Chrome's local storage (encrypted by Chrome)
- Screenshots are saved locally in `screenshots/` directory
- Activities stored in local `activity_log.json` file
- No data is sent to third parties except DashScope API for AI analysis
- You control data retention and can delete all data anytime

## License

[Your License Here]

## Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: See project README and native host documentation
- **API Documentation**: [DashScope Documentation](https://help.aliyun.com/zh/dashscope/)

## Roadmap

- [ ] Chrome Web Store publication
- [ ] Safari extension port
- [ ] Web dashboard integration
- [ ] Cloud sync (optional)
- [ ] Activity search and filtering
- [ ] Custom AI prompts
- [ ] Multi-language support
- [ ] Dark mode
