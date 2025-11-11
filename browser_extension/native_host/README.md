# Native Messaging Host Installation

This directory contains the native messaging host setup for the Activity Recorder browser extension.

## What is a Native Messaging Host?

Browser extensions cannot directly access desktop features like screen capture. A native messaging host is a small application that runs on your computer and communicates with the browser extension, enabling features like:

- Full desktop screenshot capture
- Access to local file system
- Integration with system APIs

## Installation

### Automatic Installation (Recommended)

```bash
# Linux/macOS
python3 install.py

# Windows
python install.py
```

### Manual Installation

1. **Make launcher executable** (Linux/macOS only):
   ```bash
   chmod +x native_host_launcher.sh
   ```

2. **Update manifest file**:
   - Open `com.activity_recorder.host.json`
   - Replace `REPLACE_WITH_ABSOLUTE_PATH` with the actual path to `native_host_launcher.sh` (or `.bat` on Windows)
   - Replace `EXTENSION_ID_WILL_BE_REPLACED` with your actual extension ID from Chrome

3. **Copy manifest to system location**:

   **Linux:**
   ```bash
   mkdir -p ~/.config/google-chrome/NativeMessagingHosts
   cp com.activity_recorder.host.json ~/.config/google-chrome/NativeMessagingHosts/
   ```

   **macOS:**
   ```bash
   mkdir -p ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts
   cp com.activity_recorder.host.json ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/
   ```

   **Windows:**
   ```
   mkdir "%APPDATA%\Google\Chrome\NativeMessagingHosts"
   copy com.activity_recorder.host.json "%APPDATA%\Google\Chrome\NativeMessagingHosts\"
   ```

   On Windows, you may also need to add a registry key. Create a `.reg` file:
   ```reg
   Windows Registry Editor Version 5.00

   [HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.activity_recorder.host]
   @="C:\\path\\to\\com.activity_recorder.host.json"
   ```

## Verifying Installation

1. Check that the manifest file exists in the correct location
2. Check that the launcher script is executable and points to the correct Python script
3. Test by installing the browser extension and checking the console for connection errors

## Troubleshooting

### Extension can't connect to native host

- Check that `native_host.py` is in the project root
- Verify Python dependencies are installed: `pip install -r requirements.txt`
- Check the error log: `native_host_error.log` in this directory
- Verify the extension ID in `allowed_origins` matches your installed extension

### Permission denied errors (Linux/macOS)

```bash
chmod +x native_host_launcher.sh
```

### Python not found

- Make sure Python 3 is installed and in your PATH
- On Linux/macOS, verify with: `which python3`
- On Windows, verify with: `where python`

## Supported Browsers

This native host works with all Chromium-based browsers:
- Google Chrome
- Microsoft Edge
- Brave
- Chromium
- Opera

For other browsers (Firefox, Safari), different manifest formats and installation locations are required.

## Uninstallation

```bash
python3 install.py uninstall
```

This will remove the manifest file from the system location. You may also want to delete this directory if you're completely removing the application.
