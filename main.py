import threading
import logging

from bot import run_bot
from app import run_web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Run both the Telegram bot and the Flask web server."""
    logger.info("Starting Call OSINT services...")

    # Run Flask in a separate thread
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    logger.info("Web server started on port 5000")

    # Run bot in main thread
    logger.info("Starting Telegram bot...")
    run_bot()


if __name__ == "__main__":
    main()
