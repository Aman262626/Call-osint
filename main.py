import threading
import logging
import os

from bot import run_bot
from app import app

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_web():
    """Run Flask web server."""
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


def main():
    """Run both the Telegram bot and the Flask web server."""
    logger.info("Starting Call OSINT services...")

    # Run Flask in a separate thread (for Render health checks)
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    logger.info("Web server started")

    # Run bot in main thread
    logger.info("Starting Telegram bot...")
    run_bot()


if __name__ == "__main__":
    main()
