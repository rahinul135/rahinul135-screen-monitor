# local_config.py — Persistent client configuration storage.

import os
import json
import uuid
from pathlib import Path

class LocalConfig:
    def __init__(self):
        self.appdata_dir = Path(os.getenv('APPDATA'), 'employee-agent')
        self.appdata_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.appdata_dir / 'client_config.json'
        self.client_id_file = self.appdata_dir / 'client_id'

    def get_or_create_client_id(self) -> str:
        """Return existing client_id or create a new one."""
        if self.client_id_file.exists():
            return self.client_id_file.read_text().strip()
        client_id = str(uuid.uuid4())
        self.client_id_file.write_text(client_id)
        return client_id

    def load_config(self, client_id: str) -> dict:
        """Load client configuration from backend or local cache.

        Args:
            client_id: The unique identifier for this client.

        Returns:
            dict: Configuration data with default values if not set.
        """
        default_config = {
            'interval_minutes': 3,
            'bot_token': '',
            'chat_id': '',
            'send_enabled': False,
            'is_active': True,
        }
        try:
            import requests
            url = f'https://screen-monitor-cc1w.onrender.com/config/{client_id}'
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                server_config = response.json()
                # Merge server config with defaults, server data takes precedence
                merged = default_config.copy()
                merged.update(server_config)
                return merged
        except Exception as e:
            print(f'Warning: Could not fetch config from backend: {e}')
        return default_config

    def save_local_state(self, client_id: str, state: dict) -> None:
        """Save a local state snapshot for offline recovery."""
        state_data = {
            'client_id': client_id,
            'last_seen': state.get('last_seen'),
            'config': state.get('config'),
            'screenshots_sent': state.get('screenshots_sent', 0),
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f'Error saving local state: {e}')

    def load_local_state(self) -> dict:
        """Load local state from disk.

        Returns:
            dict: Previously saved state data or empty dict if not found.
        """
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f'Error loading local state: {e}')
            return {}