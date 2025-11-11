# Migration Guide: PyQt Desktop App → Browser Extension

This guide helps existing users of the PyQt desktop application migrate to the new browser-based architecture.

## Why Migrate?

The new browser extension architecture offers several advantages:

✅ **Better Integration**: Control from browser toolbar, no separate desktop window
✅ **Modern UI**: React-based web dashboard with responsive design
✅ **Cross-Platform**: Works identically on Windows, macOS, and Linux
✅ **Future-Proof**: Browser extensions are actively maintained and updated
✅ **Full Desktop Capture**: Still captures entire desktop (not just browser)
✅ **Same Backend**: Uses the same proven Python backend and AI models

## What Changes?

### Before (PyQt App)

```
User → PyQt GUI → Python Backend → DashScope API
                     ↓
              activity_log.json
```

### After (Browser Extension)

```
User → Browser Extension → Native Host (Python) → DashScope API
                                  ↓
                           activity_log.json
                                  ↓
                           Web Dashboard (optional)
```

## Migration Steps

### 1. Backup Your Data

Before migrating, backup your existing data:

```bash
cd auto_record_my_activates

# Backup activity log
cp activity_log.json activity_log.backup.json

# Backup screenshots
cp -r screenshots/ screenshots_backup/

# Backup GUI config
cp gui_config.json gui_config.backup.json
```

### 2. Update Dependencies

The browser extension uses the same Python backend, but you need to ensure all dependencies are up to date:

```bash
# Update requirements
pip install -r requirements.txt --upgrade

# Or with uv
uv pip install -r requirements.txt --upgrade
```

### 3. Install Native Messaging Host

This is the new component that enables browser communication:

```bash
cd browser_extension/native_host
python install.py
```

**What this does:**
- Registers the native messaging host with Chrome/Chromium browsers
- Creates manifest file in system location
- Sets up launcher scripts

### 4. Install Browser Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `browser_extension/chrome/` directory
5. The extension will appear in your toolbar

### 5. Update Native Host Manifest

After installing the extension:

1. Copy the **Extension ID** from the extension card
2. Edit `browser_extension/native_host/com.activity_recorder.host.json`
3. Replace `EXTENSION_ID_WILL_BE_REPLACED` with your actual extension ID
4. Run `python install.py` again to update the registration

### 6. Migrate Settings

Your existing settings from `gui_config.json` need to be transferred to the browser extension:

**GUI Config (Old)** → **Extension Settings (New)**

| Old Setting | New Location | How to Set |
|-------------|--------------|------------|
| API Key | Extension Options | Click extension → Settings → Enter API key |
| Screenshot Interval | Extension Options | Click extension → Settings → Capture Interval |
| Model Name | Extension Options | Click extension → Settings → AI Model dropdown |
| Auto Start | Extension Options | Click extension → Settings → Auto-start Recording toggle |
| Thinking Mode | Extension Options | Click extension → Settings → Enable Thinking Mode |
| Retention Days | Extension Options | Click extension → Settings → Data Retention |

**To open Extension Settings:**
1. Click the extension icon in toolbar
2. Click "Settings" link in popup
3. Configure all settings
4. Click "Save Settings"

### 7. Start Using the Extension

1. Click the extension icon in your browser toolbar
2. Click "Start Recording"
3. Screenshots will be captured automatically
4. View activities by clicking "View Dashboard" (requires web dashboard setup)

### 8. Optional: Set Up Web Dashboard

The web dashboard provides a modern interface for viewing activities:

```bash
cd web_dashboard
npm install
npm run dev
```

Open `http://localhost:3000` to view your activities.

## Data Compatibility

### Good News: Existing Data Works!

Your existing `activity_log.json` and screenshots are **fully compatible** with the new system:

- ✅ **Same JSON Format**: The browser extension writes the same format
- ✅ **Same Screenshot Format**: PNG files in `screenshots/` directory
- ✅ **Backward Compatible**: Old activities display correctly in new dashboard
- ✅ **No Data Loss**: All existing activities are preserved

### Accessing Old Activities

**Browser Extension:**
- Click extension icon → View recent activities in popup
- Use web dashboard for full browsing

**Web Dashboard:**
- Navigate to Activities page
- Use search and filters
- Click on any activity to view details and screenshot

## Feature Comparison

| Feature | PyQt App | Browser Extension | Notes |
|---------|----------|-------------------|-------|
| Auto Screenshot | ✅ | ✅ | Same functionality |
| AI Analysis | ✅ | ✅ | Same models (Qwen-VL) |
| Activity Timeline | ✅ | ✅ | Better UI in web dashboard |
| Time Query | ✅ | ✅ | Improved interface |
| Settings Management | ✅ | ✅ | More intuitive in extension |
| System Tray | ✅ | ✅ | Browser toolbar instead |
| Screenshot Preview | ✅ | ✅ | Better zoom in web dashboard |
| Data Export | ✅ | ✅ | Same functionality |
| Minimize to Tray | ✅ | N/A | Use browser minimize instead |
| Standalone App | ✅ | ❌ | Requires browser running |
| Mobile Support | ❌ | 🔜 | Planned for future |

## Troubleshooting Migration Issues

### Extension Can't Connect to Native Host

**Problem**: "Cannot connect to native host" error

**Solution**:
```bash
# Re-run installer
cd browser_extension/native_host
python install.py

# Verify manifest file exists
# Linux: ~/.config/google-chrome/NativeMessagingHosts/
# macOS: ~/Library/Application Support/Google/Chrome/NativeMessagingHosts/
# Windows: %APPDATA%\Google\Chrome\NativeMessagingHosts/

# Check extension ID is correct in manifest
```

### Old Activities Not Showing

**Problem**: Web dashboard doesn't show old activities

**Solution**:
```bash
# Verify activity_log.json exists
ls -l activity_log.json

# For web dashboard development, copy to public/
cp activity_log.json web_dashboard/public/
cp -r screenshots/ web_dashboard/public/

# Check browser console for errors
```

### Settings Not Transferring

**Problem**: Have to re-enter all settings

**Solution**: This is expected - settings formats are different. You need to manually re-enter:
1. API Key (most important)
2. Preferred interval
3. Model selection
4. Other preferences

**Tip**: Save your `gui_config.json` as reference before migration.

### Screenshots Missing

**Problem**: Old screenshots don't appear in dashboard

**Solution**:
```bash
# Verify screenshots directory exists
ls -l screenshots/

# Check paths in activity_log.json are correct
# Should be relative paths like: "screenshots/screenshot_20250111_100300.png"

# For web dashboard, ensure screenshots are accessible:
# Option 1: Copy to public/
cp -r screenshots/ web_dashboard/public/

# Option 2: Configure server to serve screenshots directory
```

## Rolling Back

If you need to go back to the PyQt app:

```bash
# The PyQt app still works!
python main_gui.py

# Your data is unchanged
# All screenshots and activity_log.json remain intact
```

**Note**: You can run both the PyQt app and browser extension simultaneously, but:
- They'll use the same `activity_log.json` (could cause conflicts)
- Recommend using only one at a time
- Or use different data directories

## FAQ

### Do I need to uninstall the PyQt app?

No! You can keep both installed. The PyQt app code is still there and functional. You can switch between them anytime.

### Will my old screenshots still work?

Yes! The screenshot format is identical. Both systems use PNG files in the `screenshots/` directory.

### Can I export my old data?

Yes! Use the PyQt app or the new web dashboard to export activities as JSON.

### What happens to my API key?

You need to re-enter it in the extension settings. It's stored securely by Chrome.

### Do I need to keep Chrome open?

Yes, the browser extension requires the browser to be running. However:
- Chrome can run in the background
- Minimize to taskbar/dock
- Extension continues working in background

### Can I use both systems?

Not recommended simultaneously. Both write to the same files, which could cause conflicts. Choose one:
- **Use Extension**: Modern, better integrated
- **Use PyQt**: If you prefer standalone desktop app

## Getting Help

If you encounter issues during migration:

1. **Check logs**:
   - Native host: `browser_extension/native_host/native_host_error.log`
   - Extension: Chrome DevTools → Extensions → Service Worker → Console
   - Old app: `activity_recorder.log`

2. **GitHub Issues**: Report problems at https://github.com/yourusername/activity-recorder/issues

3. **Discussions**: Ask questions at https://github.com/yourusername/activity-recorder/discussions

## Recommended Next Steps

After successful migration:

1. ✅ Test recording with extension (capture a few screenshots)
2. ✅ Verify activities appear correctly
3. ✅ Set up web dashboard (optional but recommended)
4. ✅ Configure auto-start if desired
5. ✅ Customize recording interval
6. ✅ Set up data retention policies

## Conclusion

The migration is straightforward and your data is fully preserved. The new browser-based architecture offers better integration and a modern interface while maintaining all the core functionality you relied on.

Welcome to the new Activity Recorder! 🎉
