import os
import re
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID
from api_client import (
    number_lookup,
    aadhar_lookup,
    freefire_lookup,
    bgmi_lookup,
    aadhar_family,
    snapchat_lookup,
)
from pdf_generator import generate_pdf

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Input Detection ───────────────────────────────────────

def detect_input_type(text: str) -> str:
    """Auto-detect what the user entered.
    
    Returns: 'mobile', 'aadhar', 'ff_uid', 'bgmi_uid', 'snapchat'
    """
    text = text.strip()

    # 10-digit number starting with 6-9 → Indian mobile number
    if re.match(r"^[6-9]\d{9}$", text):
        return "mobile"

    # 10-digit number starting with 0-5 → BGMI UID (not Indian mobile)
    if re.match(r"^\d{10}$", text):
        return "bgmi_uid"

    # 12-digit number → Aadhar number
    if re.match(r"^\d{12}$", text):
        return "aadhar"

    # 7-9 digit number → Could be Free Fire UID
    if re.match(r"^\d{7,9}$", text):
        return "ff_uid"

    # 11 or 13+ digit number → Could be BGMI UID
    if re.match(r"^\d{11,}$", text) and len(text) != 12:
        return "bgmi_uid"

    # Pure digits of other lengths → try as game UID
    if re.match(r"^\d+$", text):
        if len(text) <= 9:
            return "ff_uid"
        return "bgmi_uid"

    # Text (non-numeric) → Snapchat username
    return "snapchat"


# ─── Formatters ────────────────────────────────────────────

def format_dict(data, indent=0) -> str:
    """Recursively format a dict/list into a readable string with emojis."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            emoji = _get_emoji_for_key(str(key).lower())
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{emoji} <b>{key}:</b>")
                lines.append(format_dict(value, indent + 1))
            else:
                lines.append(f"{prefix}{emoji} <b>{key}:</b> <code>{value}</code>")
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}📌 <b>#{i}</b>")
                lines.append(format_dict(item, indent + 1))
            else:
                lines.append(f"{prefix}▫️ <code>{item}</code>")
    else:
        lines.append(f"{prefix}<code>{data}</code>")
    return "\n".join(lines)


def _get_emoji_for_key(key: str) -> str:
    """Return an emoji based on key name."""
    emoji_map = {
        "name": "👤", "fname": "👤", "lname": "👤",
        "first_name": "👤", "last_name": "👤", "full_name": "👤",
        "father": "👨", "mother": "👩",
        "address": "🏠", "addr": "🏠",
        "state": "🗺️", "district": "🏙️", "city": "🏙️",
        "pincode": "📮", "pin": "📮", "zip": "📮",
        "dob": "🎂", "date_of_birth": "🎂", "age": "🎂",
        "gender": "⚧️", "sex": "⚧️",
        "mobile": "📱", "phone": "📱", "number": "📱", "num": "📱",
        "email": "📧", "mail": "📧",
        "aadhar": "🪪", "aadhaar": "🪪",
        "uid": "🆔", "id": "🆔",
        "pan": "💳", "voter": "🗳️",
        "photo": "📸", "image": "📸", "pic": "📸",
        "status": "✅", "result": "📊", "data": "📂", "info": "ℹ️",
        "level": "📊", "rank": "🏆", "score": "🎯",
        "kills": "💀", "wins": "🏆", "matches": "🎮",
        "guild": "⚔️", "clan": "⚔️",
        "username": "👤", "snap": "👻", "snapchat": "👻",
        "bitmoji": "🎭", "avatar": "🎭",
        "family": "👨‍👩‍👧‍👦", "relation": "🔗", "member": "👥",
        "operator": "📡", "carrier": "📡", "provider": "📡",
        "location": "📍", "country": "🌍", "region": "🌐",
        "error": "❌", "message": "💬", "msg": "💬",
    }
    for k, emoji in emoji_map.items():
        if k in key:
            return emoji
    return "🔹"


def build_section(title: str, data: dict) -> str:
    """Build a formatted section for one lookup result."""
    separator = "━" * 25
    text = f"\n{separator}\n🔍 <b>{title}</b>\n{separator}\n\n"
    text += format_dict(data)
    text += "\n"
    return text


# ─── Extract Aadhar numbers from API response ─────────────

def _extract_aadhar_numbers(data, found=None) -> list:
    """Recursively extract Aadhar numbers from API response."""
    if found is None:
        found = []
    if isinstance(data, dict):
        for key, value in data.items():
            if any(k in key.lower() for k in ["aadhar", "aadhaar", "adhar", "uid_number"]):
                if isinstance(value, str) and len(value) == 12 and value.isdigit():
                    if value not in found:
                        found.append(value)
            elif isinstance(value, (dict, list)):
                _extract_aadhar_numbers(value, found)
    elif isinstance(data, list):
        for item in data:
            _extract_aadhar_numbers(item, found)
    return found


def _extract_numbers(data, found=None) -> list:
    """Recursively extract mobile numbers from API response."""
    if found is None:
        found = []
    if isinstance(data, dict):
        for key, value in data.items():
            if any(k in key.lower() for k in ["mobile", "phone", "number", "num", "contact"]):
                if isinstance(value, str) and len(value) == 10 and value.isdigit():
                    if value not in found:
                        found.append(value)
            elif isinstance(value, (dict, list)):
                _extract_numbers(value, found)
    elif isinstance(data, list):
        for item in data:
            _extract_numbers(item, found)
    return found


# ─── Auto Chain Lookup ─────────────────────────────────────

async def auto_chain_mobile(number: str, update: Update):
    """Full auto chain: Mobile → Number Info → Aadhar → Aadhar Info → Family."""
    sections = []
    all_text = ""

    separator = "━" * 25
    header = f"""
{separator}
🔥 <b>AUTO OSINT SCAN</b> 🔥
📱 <b>Input:</b> <code>{number}</code>
🔎 <b>Type:</b> Mobile Number
{separator}
"""
    all_text += header

    # Step 1: Number Lookup
    step_msg = await update.message.reply_text(
        "⏳ <b>Step 1/3:</b> 📱 Number Lookup...", parse_mode="HTML"
    )
    try:
        num_data = number_lookup(number)
        section = build_section("📱 STEP 1 — Number Lookup", num_data)
        all_text += section
        await safe_send(update, section)
    except Exception as e:
        num_data = {}
        all_text += f"\n❌ Number Lookup Failed: {e}\n"
        await update.message.reply_text(f"❌ Number Lookup Error: <code>{e}</code>", parse_mode="HTML")

    await step_msg.delete()

    # Step 2: Extract Aadhar & lookup
    aadhar_nums = _extract_aadhar_numbers(num_data)
    if aadhar_nums:
        step_msg = await update.message.reply_text(
            f"⏳ <b>Step 2/3:</b> 🪪 Found {len(aadhar_nums)} Aadhar(s) — Looking up...",
            parse_mode="HTML",
        )
        for aadhar_num in aadhar_nums:
            try:
                aadhar_data = aadhar_lookup(aadhar_num)
                section = build_section(f"🪪 STEP 2 — Aadhar Lookup ({aadhar_num})", aadhar_data)
                all_text += section
                await safe_send(update, section)
            except Exception as e:
                all_text += f"\n❌ Aadhar Lookup ({aadhar_num}) Failed: {e}\n"

            # Step 3: Family search from each Aadhar
            try:
                family_data = aadhar_family(aadhar_num)
                section = build_section(f"👨‍👩‍👧‍👦 STEP 3 — Family Search ({aadhar_num})", family_data)
                all_text += section
                await safe_send(update, section)
            except Exception as e:
                all_text += f"\n❌ Family Search ({aadhar_num}) Failed: {e}\n"

        await step_msg.delete()
    else:
        await update.message.reply_text(
            "ℹ️ <b>Step 2:</b> No Aadhar found in number data — skipping Aadhar & Family lookup",
            parse_mode="HTML",
        )

    # Footer
    footer = f"""
{separator}
✅ <b>SCAN COMPLETE</b>
⏰ <i>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</i>
🤖 <b>Call OSINT Bot — Auto Scan</b>
{separator}"""
    all_text += footer
    await update.message.reply_text(footer, parse_mode="HTML")

    # Send PDF
    await send_pdf(update, f"Auto Scan — {number}", all_text)


async def auto_chain_aadhar(aadhar_num: str, update: Update):
    """Full auto chain: Aadhar → Info → Family → Extract numbers → Number lookup."""
    all_text = ""
    separator = "━" * 25

    header = f"""
{separator}
🔥 <b>AUTO OSINT SCAN</b> 🔥
🪪 <b>Input:</b> <code>{aadhar_num}</code>
🔎 <b>Type:</b> Aadhar Number
{separator}
"""
    all_text += header

    # Step 1: Aadhar lookup
    step_msg = await update.message.reply_text(
        "⏳ <b>Step 1/3:</b> 🪪 Aadhar Lookup...", parse_mode="HTML"
    )
    aadhar_data = {}
    try:
        aadhar_data = aadhar_lookup(aadhar_num)
        section = build_section("🪪 STEP 1 — Aadhar Lookup", aadhar_data)
        all_text += section
        await safe_send(update, section)
    except Exception as e:
        all_text += f"\n❌ Aadhar Lookup Failed: {e}\n"
        await update.message.reply_text(f"❌ Aadhar Lookup Error: <code>{e}</code>", parse_mode="HTML")
    await step_msg.delete()

    # Step 2: Family search
    step_msg = await update.message.reply_text(
        "⏳ <b>Step 2/3:</b> 👨‍👩‍👧‍👦 Family Search...", parse_mode="HTML"
    )
    family_data = {}
    try:
        family_data = aadhar_family(aadhar_num)
        section = build_section("👨‍👩‍👧‍👦 STEP 2 — Family Search", family_data)
        all_text += section
        await safe_send(update, section)
    except Exception as e:
        all_text += f"\n❌ Family Search Failed: {e}\n"
    await step_msg.delete()

    # Step 3: Extract mobile numbers from aadhar/family data and look them up
    all_numbers = _extract_numbers(aadhar_data) + _extract_numbers(family_data)
    unique_numbers = list(dict.fromkeys(all_numbers))

    if unique_numbers:
        step_msg = await update.message.reply_text(
            f"⏳ <b>Step 3/3:</b> 📱 Found {len(unique_numbers)} number(s) — Looking up...",
            parse_mode="HTML",
        )
        for num in unique_numbers:
            try:
                num_data = number_lookup(num)
                section = build_section(f"📱 STEP 3 — Number Lookup ({num})", num_data)
                all_text += section
                await safe_send(update, section)
            except Exception as e:
                all_text += f"\n❌ Number Lookup ({num}) Failed: {e}\n"
        await step_msg.delete()
    else:
        await update.message.reply_text(
            "ℹ️ <b>Step 3:</b> No mobile numbers found — skipping number lookup",
            parse_mode="HTML",
        )

    # Footer
    footer = f"""
{separator}
✅ <b>SCAN COMPLETE</b>
⏰ <i>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</i>
🤖 <b>Call OSINT Bot — Auto Scan</b>
{separator}"""
    all_text += footer
    await update.message.reply_text(footer, parse_mode="HTML")
    await send_pdf(update, f"Auto Scan — {aadhar_num}", all_text)


async def single_lookup(input_text: str, lookup_type: str, update: Update):
    """Single lookup for FF, BGMI, Snapchat."""
    separator = "━" * 25
    type_labels = {
        "ff_uid": ("🎮 Free Fire Lookup", freefire_lookup),
        "bgmi_uid": ("🎯 BGMI Lookup", bgmi_lookup),
        "snapchat": ("👻 Snapchat Lookup", snapchat_lookup),
    }

    label, lookup_fn = type_labels[lookup_type]

    step_msg = await update.message.reply_text(
        f"⏳ <b>{label}...</b>", parse_mode="HTML"
    )
    try:
        data = lookup_fn(input_text)
        section = build_section(f"{label} — {input_text}", data)

        footer = f"""
{separator}
✅ <b>LOOKUP COMPLETE</b>
⏰ <i>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</i>
🤖 <b>Call OSINT Bot</b>
{separator}"""

        full_text = section + footer
        await safe_send(update, full_text)
        await send_pdf(update, f"{label} — {input_text}", full_text)
    except Exception as e:
        await update.message.reply_text(
            f"❌ <b>{label} Error:</b> <code>{e}</code>", parse_mode="HTML"
        )
    await step_msg.delete()


# ─── Message Utilities ─────────────────────────────────────

async def safe_send(update: Update, text: str):
    """Send a long message, splitting if needed (Telegram limit is 4096 chars)."""
    if len(text) <= 4096:
        await update.message.reply_text(text, parse_mode="HTML")
    else:
        parts = []
        while text:
            if len(text) <= 4096:
                parts.append(text)
                break
            split_at = text[:4096].rfind("\n")
            if split_at == -1:
                split_at = 4096
            parts.append(text[:split_at])
            text = text[split_at:]
        for part in parts:
            if part.strip():
                await update.message.reply_text(part, parse_mode="HTML")


async def send_pdf(update: Update, title: str, text: str):
    """Generate and send a PDF of the result."""
    try:
        pdf_path = generate_pdf(title, text)
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename=f"OSINT_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                caption="📄 <b>PDF Report — Download karo!</b>",
                parse_mode="HTML",
            )
        os.unlink(pdf_path)
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        await update.message.reply_text(
            f"⚠️ <i>PDF generation failed: {e}</i>", parse_mode="HTML"
        )


# ─── Bot Handlers ──────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 <b>CALL OSINT BOT</b> 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ <b>Advanced Auto OSINT Tool</b>

💡 <b>Koi bhi cheez daalo — Bot khud detect karega!</b>

📱 <b>10-digit number</b> → Mobile Lookup → Aadhar → Family (Auto Chain)
🪪 <b>12-digit number</b> → Aadhar Lookup → Family → Numbers (Auto Chain)
🎮 <b>7-9 digit number</b> → Free Fire UID Lookup
🎯 <b>10+ digit (non-mobile)</b> → BGMI UID Lookup
👻 <b>Text/username</b> → Snapchat Lookup

━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sirf ek input daalo — baaki sab auto!</b>
📄 <b>Har result ka PDF bhi milega!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━

👇 <i>Abhi kuch bhi type karo ya button click karo!</i>
"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Number Scan", callback_data="hint_number"),
            InlineKeyboardButton("🪪 Aadhar Scan", callback_data="hint_aadhar"),
        ],
        [
            InlineKeyboardButton("🎮 Free Fire", callback_data="hint_ff"),
            InlineKeyboardButton("🎯 BGMI", callback_data="hint_bgmi"),
        ],
        [
            InlineKeyboardButton("👻 Snapchat", callback_data="hint_snap"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
🆘 <b>HELP — Call OSINT Bot</b>

💡 <b>Auto-Detect Mode (Default):</b>
Sirf kuch bhi type karo — bot khud samjh jayega!

📱 <b>Mobile Number (10 digits)</b>
   → Auto: Number → Aadhar → Family

🪪 <b>Aadhar Number (12 digits)</b>
   → Auto: Aadhar → Family → Numbers

🎮 <b>Free Fire UID (7-9 digits)</b>
   → Player info lookup

🎯 <b>BGMI UID (10+ digits)</b>
   → Player info lookup

👻 <b>Snapchat Username (text)</b>
   → Profile lookup

━━━━━━━━━━━━━━━━━━━━━━━━━
📄 <b>Har result ka PDF auto milega!</b>
⚡ <b>Koi command ki zaroorat nahi!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(help_text, parse_mode="HTML")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard buttons — just show hints."""
    query = update.callback_query
    await query.answer()

    hints = {
        "hint_number": "📱 <b>Mobile number type karo (10 digits):</b>\n\n<i>Example: 9876543210</i>\n\n⚡ Auto: Number → Aadhar → Family sab nikal aayega!",
        "hint_aadhar": "🪪 <b>Aadhar number type karo (12 digits):</b>\n\n<i>Example: 393933081942</i>\n\n⚡ Auto: Aadhar → Family → Numbers sab nikal aayega!",
        "hint_ff": "🎮 <b>Free Fire UID type karo (7-9 digits):</b>\n\n<i>Example: 123456789</i>",
        "hint_bgmi": "🎯 <b>BGMI UID type karo:</b>\n\n<i>Example: 5121439477</i>\n\n💡 <i>10-digit UID jo 0-5 se start ho = BGMI\n10-digit jo 6-9 se start ho = Mobile</i>",
        "hint_snap": "👻 <b>Snapchat username type karo:</b>\n\n<i>Example: priyapanchal272</i>",
    }

    hint = hints.get(query.data, "Kuch bhi type karo!")
    await query.message.reply_text(hint, parse_mode="HTML")


async def auto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any text message — auto-detect and process."""
    text = update.message.text.strip()

    if not text or text.startswith("/"):
        return

    input_type = detect_input_type(text)

    # Show what was detected
    type_names = {
        "mobile": "📱 Mobile Number",
        "aadhar": "🪪 Aadhar Number",
        "ff_uid": "🎮 Free Fire UID",
        "bgmi_uid": "🎯 BGMI UID",
        "snapchat": "👻 Snapchat Username",
    }

    detect_msg = await update.message.reply_text(
        f"🔎 <b>Detected:</b> {type_names[input_type]}\n⚡ <b>Auto scanning...</b>",
        parse_mode="HTML",
    )

    if input_type == "mobile":
        await auto_chain_mobile(text, update)
    elif input_type == "aadhar":
        await auto_chain_aadhar(text, update)
    else:
        await single_lookup(text, input_type, update)

    try:
        await detect_msg.delete()
    except Exception:
        pass


def run_bot():
    """Start the Telegram bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_handler))

    logger.info("🤖 Bot started — Auto-detect mode!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()
