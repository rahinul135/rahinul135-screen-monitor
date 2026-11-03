# updater.py — Checks for and applies updates to the agent.

import requests
import hashlib
import os
import shutil
import subprocess
import time
import logging
from pathlib import Path
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

class Updater:
    def __init__(self, current_version: str, backend_url: str, executable_path: str, client_id: str):
        self.current_version = current_version
        self.backend_url = backend_url
        self.executable_path = executable_path
        self.client_id = client_id
        self.interval = 600  # seconds
        self.running = True
        self.logger = logger

    def start(self) -> None:
        """Start the update checker thread."""
        self.logger.info(f'Starting update checker for client {self.client_id}')
        thread = threading.Thread(target=self._check_for_updates, daemon=True)
        thread.start()

    def _check_for_updates(self) -> None:
        """Check for updates and apply them if found."""
        while self.running:
            try:
                url = f'{self.backend_url}/update/latest'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    update_info = response.json()
                    latest_version = update_info.get('version')
                    download_url = update_info.get('url')
                    checksum = update_info.get('sha256')

                    if latest_version and self._should_update(latest_version):
                        self.logger.info(f'New version {latest_version} available for client {self.client_id}')
                        self._apply_update(download_url, checksum)
                    else:
                        self.logger.debug(f'No update needed for client {self.client_id}')
                else:
                    self.logger.warning(f'Failed to check for updates. Status code: {response.status_code}, Response: {response.text}')
            except Exception as e:
                self.logger.error(f'Error checking for updates: {e}')
            time.sleep(self.interval)

    def _should_update(self, latest_version: str) -> bool:
        """Determine if an update is needed based on version comparison."""
        # Simple version comparison (assumes semantic versioning)
        return latest_version != self.current_version

    def _apply_update(self, download_url: str, checksum: str) -> None:
        """Download and apply the update."""
        try:
            self.logger.info(f'Downloading update from {download_url}')
            response = requests.get(download_url, timeout=60)
            if response.status_code == 200:
                temp_file = os.path.join(os.getenv('TEMP'), f'agent_update_{int(time.time())}.exe')
                with open(temp_file, 'wb') as f:
                    f.write(response.content)

                if checksum and self._verify_checksum(temp_file, checksum):
                    self.logger.info('Checksum verified, applying update')
                    self._restart_with_new_version(temp_file)
                else:
                    self.logger.error('Checksum verification failed, skipping update')
                    os.remove(temp_file)
            else:
                self.logger.error(f'Failed to download update. Status code: {response.status_code}')
        except Exception as e:
            self.logger.error(f'Error applying update: {e}')

    def _verify_checksum(self, filepath: str, expected_checksum: str) -> bool:
        """Verify the SHA256 checksum of the downloaded file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256_hash.update(chunk)
            calculated_checksum = sha256_hash.hexdigest()
            return calculated_checksum.lower() == expected_checksum.lower()
        except Exception as e:
            self.logger.error(f'Error verifying checksum: {e}')
            return False

    def _restart_with_new_version(self, new_executable_path: str) -> None:
        """Replace the current executable with the new one and restart."""
        try:
            # Create a batch file to perform the update
            batch_file = os.path.join(os.getenv('TEMP'), f'agent_update_{int(time.time())}.bat')
            with open(batch_file, 'w') as f:
                f.write(f'''@echo off
timeout /t 5 /nobreak >nul
copy /Y "{new_executable_path}" "{self.executable_path}"
start "" "{self.executable_path}"
del "%~f0"
''')

            self.logger.info(f'Update prepared, waiting before restart')
            # Wait for a few seconds to ensure the current process can exit cleanly
            time.sleep(5)

            # Execute the batch file
            subprocess.run(batch_file, shell=True, check=True)
            self.logger.info('Update applied successfully')
        except Exception as e:
            self.logger.error(f'Error restarting with new version: {e}')

    def stop(self) -> None:
        """Stop the update checker thread."""
        self.running = False
        self.logger.info('Stopping update checker')