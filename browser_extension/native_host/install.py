#!/usr/bin/env python3
"""
Native Host Installer

This script installs the native messaging host for Chrome/Chromium browsers.
It copies the manifest file to the correct location and updates the paths.
"""

import os
import sys
import json
import platform
from pathlib import Path


def get_manifest_dir():
    """Get the native messaging host manifest directory for the current platform"""
    system = platform.system()

    if system == "Linux":
        return Path.home() / ".config" / "google-chrome" / "NativeMessagingHosts"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts"
    elif system == "Windows":
        # On Windows, we need to use registry, but we'll also create the file
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Google" / "Chrome" / "NativeMessagingHosts"
        return None
    else:
        return None


def install_manifest():
    """Install the native messaging host manifest"""
    # Get paths
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent
    manifest_template = script_dir / "com.activity_recorder.host.json"

    # Determine launcher script based on platform
    system = platform.system()
    if system == "Windows":
        launcher_script = script_dir / "native_host_launcher.bat"
    else:
        launcher_script = script_dir / "native_host_launcher.sh"

    # Make launcher executable on Unix systems
    if system in ["Linux", "Darwin"]:
        os.chmod(launcher_script, 0o755)

    # Read manifest template
    with open(manifest_template, 'r') as f:
        manifest = json.load(f)

    # Update manifest with actual paths
    manifest["path"] = str(launcher_script)

    # Get manifest directory
    manifest_dir = get_manifest_dir()
    if not manifest_dir:
        print(f"Unsupported platform: {system}")
        return False

    # Create manifest directory if it doesn't exist
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Write manifest file
    manifest_file = manifest_dir / "com.activity_recorder.host.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Native messaging host installed successfully!")
    print(f"  Manifest location: {manifest_file}")
    print(f"  Launcher script: {launcher_script}")
    print(f"  Project root: {project_root}")

    # Windows-specific instructions
    if system == "Windows":
        print("\nNote: On Windows, you may also need to add a registry key.")
        print("Run install_registry.bat as administrator to complete the installation.")

    # Chromium-based browsers
    print("\nThis installation works for:")
    print("  - Google Chrome")
    print("  - Microsoft Edge")
    print("  - Brave")
    print("  - Other Chromium-based browsers")

    return True


def uninstall_manifest():
    """Uninstall the native messaging host manifest"""
    manifest_dir = get_manifest_dir()
    if not manifest_dir:
        print("Unsupported platform")
        return False

    manifest_file = manifest_dir / "com.activity_recorder.host.json"

    if manifest_file.exists():
        manifest_file.unlink()
        print(f"✓ Native messaging host uninstalled successfully!")
        print(f"  Removed: {manifest_file}")
        return True
    else:
        print("Native messaging host is not installed")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_manifest()
    else:
        print("Activity Recorder - Native Messaging Host Installer")
        print("=" * 55)
        print()

        install_manifest()

        print()
        print("Next steps:")
        print("1. Install the browser extension from chrome://extensions")
        print("2. Copy the extension ID from the extension details")
        print("3. Update the manifest file to include the extension ID in 'allowed_origins'")


if __name__ == "__main__":
    main()
