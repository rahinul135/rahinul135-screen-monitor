# screenshot.py — Silent screen capture using the mss library.

import mss
import mss.windows
from PIL import Image
import os
from datetime import datetime
import logging

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

class ScreenshotManager:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.getenv('APPDATA'), 'employee-agent', 'screenshots')
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = logger

    def capture_screenshot(self) -> str:
        """Capture the entire screen silently and save to disk.

        Returns:
            str: Path to the saved screenshot file.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{timestamp}.jpg'
        filepath = os.path.join(self.output_dir, filename)

        try:
            # Use mss to capture screen without flashing
            with mss.mss() as sct:
                # Capture the whole screen
                monitor = {'top': 0, 'left': 0, 'width': sct.monitors[1]['width'], 'height': sct.monitors[1]['height']}
                img = sct.grab(monitor)

                # Convert to PIL Image and save as JPEG with compression
                pil_img = Image.frombytes('RGB', img.size, img.rgb)
                pil_img.save(filepath, format='JPEG', quality=70, optimize=True)

            self.logger.info(f'Screenshot captured and saved to {filepath}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to capture screenshot: {e}')
            raise

    def cleanup_old_screenshots(self, max_files: int = 50) -> None:
        """Remove old screenshot files to manage disk space."""
        try:
            files = sorted(os.listdir(self.output_dir), reverse=True)
            for f in files[max_files:]:
                os.remove(os.path.join(self.output_dir, f))
                self.logger.info(f'Removed old screenshot: {f}')
        except Exception as e:
            self.logger.error(f'Error during cleanup: {e}')