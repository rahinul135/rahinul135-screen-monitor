# config_poller.py — Polls the backend for configuration updates.

import os
import requests
import time
import logging
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getenv('APPDATA'), 'employee-agent', 'agent.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConfigPoller:
    def __init__(self, client_id: str, backend_url: str, callback):
        self.client_id = client_id
        self.backend_url = backend_url
        self.callback = callback
        self.interval = 60  # seconds
        self.running = True
        self.logger = logger

    def start(self) -> None:
        """Start the configuration polling thread."""
        self.logger.info(f'Starting config poller for client {self.client_id}')
        thread = threading.Thread(target=self._poll_config, daemon=True)
        thread.start()

    def _poll_config(self) -> None:
        """Poll the backend for configuration updates."""
        last_config = {}
        while self.running:
            try:
                url = f'{self.backend_url}/config/{self.client_id}'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    new_config = response.json()
                    # Check if config has changed
                    if new_config != last_config:
                        self.logger.info(f'New configuration received for client {self.client_id}: {new_config}')
                        self.callback(new_config)
                        last_config = new_config
                    else:
                        self.logger.debug(f'No configuration changes for client {self.client_id}')
                else:
                    self.logger.warning(f'Failed to fetch configuration. Status code: {response.status_code}, Response: {response.text}')
            except Exception as e:
                self.logger.error(f'Error polling configuration: {e}')
            time.sleep(self.interval)

    def stop(self) -> None:
        """Stop the configuration polling thread."""
        self.running = False
        self.logger.info('Stopping config poller')