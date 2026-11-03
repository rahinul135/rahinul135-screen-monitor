# heartbeat.py — Sends periodic heartbeat signals to the backend to indicate client is alive.

import os
import requests
import time
import logging
from datetime import datetime
import threading
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getenv('APPDATA'), 'employee-agent', 'agent.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HeartbeatManager:
    def __init__(self, client_id: str, backend_url: str):
        self.client_id = client_id
        self.backend_url = backend_url
        self.interval = 30  # seconds
        self.running = True
        self.logger = logger

    def start(self) -> None:
        """Start the heartbeat thread."""
        self.logger.info(f'Starting heartbeat thread for client {self.client_id}')
        thread = threading.Thread(target=self._send_heartbeat, daemon=True)
        thread.start()

    def _send_heartbeat(self) -> None:
        """Send heartbeat to the backend until stopped."""
        while self.running:
            try:
                url = f'{self.backend_url}/heartbeat'
                payload = {
                    'client_id': self.client_id,
                    'timestamp': datetime.utcnow().isoformat(),
                }
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f'Heartbeat sent successfully to backend for client {self.client_id}')
                else:
                    self.logger.warning(f'Heartbeat failed. Status code: {response.status_code}, Response: {response.text}')
            except Exception as e:
                self.logger.error(f'Error sending heartbeat: {e}')
            time.sleep(self.interval)

    def stop(self) -> None:
        """Stop the heartbeat thread."""
        self.running = False
        self.logger.info('Stopping heartbeat thread')