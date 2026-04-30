import threading
import time
import logging
import os
import sys

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
    """Start the Telegram bot in a separate thread."""
    bot_token = os.environ.get("BOT_TOKEN", "").strip()

    if not bot_token:
        logger.warning("=" * 50)
        logger.warning("BOT_TOKEN not set!")
        logger.warning("Telegram bot DISABLED — only web server running")
        logger.warning("Set BOT_TOKEN in Render Environment Variables")
        logger.warning("=" * 50)
        return

    logger.info("BOT_TOKEN found — starting Telegram bot...")

    try:
        from bot import run_bot
        run_bot()
    except Exception as e:
        logger.error("=" * 50)
        logger.error("TELEGRAM BOT CRASHED!")
        logger.error("Error: %s", str(e))
        logger.error("Bot will not run, but web server continues")
        logger.error("=" * 50)
        import traceback
        traceback.print_exc()


def main():
    """Run both the Telegram bot and the Flask web server."""
    logger.info("=" * 50)
    logger.info("CALL OSINT — Starting services...")
    logger.info("=" * 50)

    # Log env var status
    bot_token = os.environ.get("BOT_TOKEN", "")
    admin_id = os.environ.get("ADMIN_ID", "")
    api_key = os.environ.get("API_KEY", "")
    port = os.environ.get("PORT", "5000")

    logger.info("PORT: %s", port)
    logger.info("BOT_TOKEN: %s", "SET" if bot_token else "NOT SET")
    logger.info("ADMIN_ID: %s", "SET" if admin_id else "NOT SET")
    logger.info("API_KEY: %s", "SET" if api_key else "NOT SET")

    # Run Flask in a separate thread (for Render health checks)
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    logger.info("Web server started on port %s", port)

    # Run bot in a separate thread so web server stays alive even if bot crashes
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Keep main thread alive (so daemon threads don't die)
    logger.info("All services running. Keeping alive...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
