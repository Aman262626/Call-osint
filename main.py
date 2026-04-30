import threading
import logging
import os

from app import app

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_web():
    """Run Flask web server on Render's assigned PORT."""
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


def run_telegram_bot():
    """Start the Telegram bot (only if token is configured)."""
    bot_token = os.environ.get("BOT_TOKEN", "")
    if not bot_token:
        logger.warning("BOT_TOKEN not set — Telegram bot disabled. Only web server running.")
        return

    from bot import run_bot
    logger.info("Starting Telegram bot...")
    run_bot()


def main():
    """Run both the Telegram bot and the Flask web server."""
    logger.info("Starting Call OSINT services...")

    # Run Flask in a separate thread (for Render health checks)
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    logger.info("Web server started on port %s", os.environ.get("PORT", 5000))

    # Run bot in main thread (blocks)
    run_telegram_bot()

    # If bot is not configured, keep the process alive for the web server
    if not os.environ.get("BOT_TOKEN"):
        logger.info("Web-only mode — bot not configured")
        import time
        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()
