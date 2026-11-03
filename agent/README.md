# Employee Screen Monitor — Silent Client Agent

This directory contains the complete client-side software for the Employee Screen Monitor system.

## What It Does

Runs silently on Windows PCs to capture the screen at a configurable interval and sends screenshots to a designated Telegram group.

## Features

- **Silent screenshot capture** — mss library provides zero-flicker screen captures.
- **Configurable interval** — polls a remote backend every 60 seconds for the latest settings.
- **Per-client interval** — each client can have its own screenshot frequency.
- **Telegram delivery** — sends screenshots to assigned Telegram bots automatically.
- **No user interaction required** — background service with optional system tray icon.
- **Auto-update** — checks for new versions every 10 minutes, applies updates silently.
- **Heartbeat** — sends alive pings to the backend every 30 seconds for status tracking.
- **Flexible routing** — each client can be assigned to zero, one, or multiple bots (default is one).
- **Process disguise** — executable name configurable for stealth operation.
- **Windows auto-start** — Registry entry ensures the agent runs after each reboot.

## Directory Contents

```
agent/
├── main.py               # Entry point, orchestrates all threads
├── screenshot.py         # mss-based silent screen capture
├── sender.py             # Telegram Bot API integration
├── config_poller.py      # Poll backend for config updates
├── heartbeat.py          # 30s heartbeat sender
├── updater.py            # Check for updates, apply silently
├── tray.py               # Optional system tray icon support
├── local_config.py       # Persist client_id to file
├── constants.py          # Backend URLs, intervals, filenames
├── requirements.txt      # Python dependencies
└── build/                # PyInstaller packaging files
```

## Installation

1. **Build the .exe:**
   On any Windows machine with Python installed:

   ```bash
   cd agent
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m pip install pyinstaller
   pyinstaller --onefile --windowed main.py
   ```

   The build output will be in `dist/main.exe` (or whatever you named the script).

2. **Deploy the .exe:**
   Copy `dist/main.exe` to the target Windows PC(s) you want to monitor.

3. **Run once:**
   Double-click `main.exe`. It will:

   - Register itself with the backend (first run only)
   - Create a `client_id` file in the user\s AppData folder
   - Start background threads
   - Launch silently in the system tray (if enabled)

## Configuration

The agent reads its initial settings from the backend on first run and polls every 60 seconds for updates. Configuration is entirely managed by the admin dashboard:

- **Interval minutes** — how often to capture and send screenshots.
- **Bot assignment** — which Telegram bot (and thus which group) receives the screenshot.
- **Active status** — enable/disable the client without uninstalling.

## Configuration File

The agent stores its `client_id` (UUID) locally at:

```
%APPDATA%\\agent\\client_id
```

This file is needed for all subsequent backend API calls.

## Development

To work on this project locally on Windows:

1. `cd agent`
2. `python -m pip install -r requirements.txt`
3. `python main.py`  (runs the console version)
4. For the GUI tray version:

   - Modify `main.py` to launch the tray version (see notes below)
   - Run again after building the tray icon

## Notes for Development

### Silent Screenshot Capture

The `screenshot.py` uses the `mss` library which is optimized for fast, silent screen captures on Windows.

Key points:

- The `mss` library does not flash the screen or cause visual interruptions.
- It captures the entire screen (or a specified monitor) depending on your configuration.

### Telegram Integration

The `sender.py` uses the `requests` library to send photos via the Telegram Bot API. It supports:

- Compressed JPEG images (quality set to 70%)
- Automatic retries on failure
- Thumbnail and file size optimization

### Process Disguise

The executable name can be configured in `constants.py` to help hide the process. This is purely cosmetic and does not affect functionality.

### System Tray Support

The `tray.py` implements a system tray icon for pausing/resuming the screenshot capture. It uses the `pystray` library for cross-platform tray support.

To run with the tray icon, modify `main.py` to call `tray.run()` instead of the console version.

### Local Configuration File

The `local_config.py` provides a simple interface to read/write the client\s configuration. This includes the `client_id` and any additional settings that need to be persisted across sessions.

### Building for Production

The build directory contains all the necessary files to create a Windows executable:

1. `main.py` - Python entry point
2. `main.spec` - PyInstaller spec file
3. `icon.ico` - Application icon (if any)

The build process should be performed on a Windows machine to generate the .exe file. The spec file can be customized to adjust the build output.

### Compatibility

This agent is designed to run on Windows 10 and newer. It may work on Windows 8 and older versions but has not been tested on those systems.

## Requirements

See `requirements.txt` for the list of Python libraries used by the agent.

## License

This project is licensed under the MIT License.