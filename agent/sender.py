# sender.py — Handles sending screenshots to Telegram via Bot API.

import requests
import os
from pathlib import Path
import logging
from datetime import datetime

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

class TelegramSender:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        self.logger = logger

    def send_screenshot(self, filepath: str, caption: str = None) -> bool:
        """Send a screenshot to Telegram.

        Args:
            filepath: Path to the image file.
            caption: Optional caption for the message.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(filepath):
            self.logger.error(f'File not found: {filepath}')
            return False

        try:
            with open(filepath, 'rb') as f:
                files = {'photo': (os.path.basename(filepath), f, 'image/jpeg')}
                data = {}
                if caption:
                    data['caption'] = caption
                response = requests.post(self.api_url, files=files, data=data, timeout=30)

                if response.status_code == 200:
                    self.logger.info(f'Screenshot sent successfully to Telegram group.')
                    return True
                else:
                    self.logger.error(f'Failed to send screenshot. Status code: {response.status_code}, Response: {response.text}')
                    return False

        except Exception as e:
            self.logger.error(f'Error sending screenshot to Telegram: {e}')
            return False

    def get_file_info(self) -> dict:
        """Get information about the Telegram bot and chat."""
        try:
            # Get bot information
            bot_info_url = f'https://api.telegram.org/bot{self.bot_token}/getMe'
            bot_response = requests.get(bot_info_url, timeout=10)
            bot_info = bot_response.json() if bot_response.status_code == 200 else None

            # Get chat information
            chat_info_url = f'https://api.telegram.org/bot{self.bot_token}/getChat'
            chat_params = {'chat_id': self.chat_id}
            chat_response = requests.get(chat_info_url, params=chat_params, timeout=10)
            chat_info = chat_response.json() if chat_response.status_code == 200 else None

            return {
                'bot_username': bot_info.get('result', {}).get('username') if bot_info else None,
                'chat_title': chat_info.get('result', {}).get('title') if chat_info else None,
                'chat_type': chat_info.get('result', {}).get('type') if chat_info else None,
            }
        except Exception as e:
            self.logger.error(f'Error getting Telegram bot/chat info: {e}')
            return {}