# tray.py — System tray integration for the agent.

import pystray
from PIL import Image, ImageDraw
import os
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

class SystemTray:
    def __init__(self, on_click_callback, on_stop_callback):
        self.icon = pystray.Icon(
            name="Employee Screen Monitor",
            title="Employee Screen Monitor",
            icon=self._create_icon(),
            menu=[
                pystray.MenuItem("Status", lambda: self._show_status()),
                pystray.MenuItem("Start/Stop Screenshot", self._toggle_screenshot, default=True),
                pystray.MenuItem("Exit", self._exit),
            ]
        )
        self.on_click_callback = on_click_callback
        self.on_stop_callback = on_stop_callback
        self.screenshot_enabled = True
        self.logger = logger

    def _create_icon(self) -> Image:
        """Create a simple icon for the tray.

        Returns:
            Image: The icon image.
        """
        image = Image.new('RGB', (64, 64), color='green')
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill='green')
        return image

    def start(self) -> None:
        """Start the system tray icon."""
        self.icon.run()

    def stop(self) -> None:
        """Stop the system tray icon."""
        self.icon.stop()

    def _show_status(self) -> None:
        """Show the current status of the agent."""
        status_message = f"Employee Screen Monitor is {self.screenshot_enabled and 'enabled' or 'disabled'} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.logger.info(status_message)
        # Show a notification (optional)
        # self.icon.notify(title='Status', message=status_message)

    def _toggle_screenshot(self) -> None:
        """Toggle the screenshot capture on/off."""
        self.screenshot_enabled = not self.screenshot_enabled
        action = 'enabled' if self.screenshot_enabled else 'disabled'
        self.logger.info(f'Screenshot capture {action}')
        self.on_click_callback(self.screenshot_enabled)

    def _exit(self) -> None:
        """Exit the application."""
        self.logger.info('Exiting')
        self.on_stop_callback()
        self.icon.stop()