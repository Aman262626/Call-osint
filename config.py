import os

# Telegram Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# OSINT API Configuration
API_KEY = os.environ.get("API_KEY", "")
API_BASE = os.environ.get("API_BASE", "https://ft-osint-api.duckdns.org/api")

# Flask Configuration
FLASK_PORT = int(os.environ.get("PORT", "5000"))
