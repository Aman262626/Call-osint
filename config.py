import os

# Telegram Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8491544250:AAEUCsJ_lT_2oNQWq4CcI0b2-x6g2h_2DvM")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5451167865"))

# OSINT API Configuration
API_KEY = os.environ.get("API_KEY", "ft-key-tr-jzynhifn87aq")
API_BASE = os.environ.get("API_BASE", "https://ft-osint-api.duckdns.org/api")

# Flask Configuration
FLASK_PORT = int(os.environ.get("PORT", "5000"))
