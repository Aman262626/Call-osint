import json
import os
import tempfile
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
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

# Conversation states
WAITING_INPUT = 0
current_action = {}


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
        "name": "👤",
        "fname": "👤",
        "lname": "👤",
        "first_name": "👤",
        "last_name": "👤",
        "full_name": "👤",
        "father": "👨",
        "mother": "👩",
        "address": "🏠",
        "addr": "🏠",
        "state": "🗺️",
        "district": "🏙️",
        "city": "🏙️",
        "pincode": "📮",
        "pin": "📮",
        "zip": "📮",
        "dob": "🎂",
        "date_of_birth": "🎂",
        "age": "🎂",
        "gender": "⚧️",
        "sex": "⚧️",
        "mobile": "📱",
        "phone": "📱",
        "number": "📱",
        "num": "📱",
        "email": "📧",
        "mail": "📧",
        "aadhar": "🪪",
        "aadhaar": "🪪",
        "uid": "🆔",
        "id": "🆔",
        "pan": "💳",
        "voter": "🗳️",
        "photo": "📸",
        "image": "📸",
        "pic": "📸",
        "status": "✅",
        "result": "📊",
        "data": "📂",
        "info": "ℹ️",
        "level": "📊",
        "rank": "🏆",
        "score": "🎯",
        "kills": "💀",
        "wins": "🏆",
        "matches": "🎮",
        "guild": "⚔️",
        "clan": "⚔️",
        "username": "👤",
        "snap": "👻",
        "snapchat": "👻",
        "bitmoji": "🎭",
        "avatar": "🎭",
        "family": "👨‍👩‍👧‍👦",
        "relation": "🔗",
        "member": "👥",
        "operator": "📡",
        "carrier": "📡",
        "provider": "📡",
        "location": "📍",
        "country": "🌍",
        "region": "🌐",
        "error": "❌",
        "message": "💬",
        "msg": "💬",
    }
    for k, emoji in emoji_map.items():
        if k in key:
            return emoji
    return "🔹"


def build_result_text(title: str, data: dict) -> str:
    """Build a beautiful formatted result message."""
    separator = "━" * 25
    header = f"""
{separator}
🔍 <b>{title}</b>
{separator}

"""
    body = format_dict(data)
    footer = f"""

{separator}
⏰ <i>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</i>
🤖 <b>Call OSINT Bot</b>
{separator}"""
    return header + body + footer


# ─── Deep Lookup (Number → Aadhar → Family) ────────────────

async def deep_lookup(number: str) -> str:
    """Perform a deep lookup: Number → Aadhar → Family."""
    results = []

    # Step 1: Number lookup
    try:
        num_data = number_lookup(number)
        results.append(("📱 Number Lookup", num_data))
    except Exception as e:
        results.append(("📱 Number Lookup", {"error": str(e)}))
        num_data = {}

    # Step 2: Try to find Aadhar from number data
    aadhar_nums = _extract_aadhar_numbers(num_data)

    if aadhar_nums:
        for aadhar_num in aadhar_nums:
            # Aadhar lookup
            try:
                aadhar_data = aadhar_lookup(aadhar_num)
                results.append((f"🪪 Aadhar Lookup ({aadhar_num})", aadhar_data))
            except Exception as e:
                results.append((f"🪪 Aadhar Lookup ({aadhar_num})", {"error": str(e)}))

            # Family lookup
            try:
                family_data = aadhar_family(aadhar_num)
                results.append((f"👨‍👩‍👧‍👦 Family Search ({aadhar_num})", family_data))
            except Exception as e:
                results.append(
                    (f"👨‍👩‍👧‍👦 Family Search ({aadhar_num})", {"error": str(e)})
                )

    # Build combined result
    separator = "━" * 25
    text = f"\n{separator}\n🔍 <b>DEEP OSINT LOOKUP</b>\n📱 <b>Number:</b> <code>{number}</code>\n{separator}\n\n"

    for title, data in results:
        text += f"▶️ <b>{title}</b>\n"
        text += format_dict(data)
        text += f"\n{'─' * 20}\n\n"

    text += f"""
{separator}
⏰ <i>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</i>
🤖 <b>Call OSINT Bot - Deep Lookup</b>
{separator}"""
    return text


def _extract_aadhar_numbers(data, found=None) -> list:
    """Recursively extract Aadhar numbers from API response."""
    if found is None:
        found = []
    if isinstance(data, dict):
        for key, value in data.items():
            if any(
                k in key.lower() for k in ["aadhar", "aadhaar", "adhar", "uid_number"]
            ):
                if isinstance(value, str) and len(value) == 12 and value.isdigit():
                    if value not in found:
                        found.append(value)
            elif isinstance(value, (dict, list)):
                _extract_aadhar_numbers(value, found)
    elif isinstance(data, list):
        for item in data:
            _extract_aadhar_numbers(item, found)
    return found


# ─── Bot Handlers ──────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome = """
━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 <b>CALL OSINT BOT</b> 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ <b>Advanced OSINT Lookup Tool</b>

📱 <b>/number</b> — Mobile Number Lookup
🪪 <b>/aadhar</b> — Aadhar Card Lookup
👨‍👩‍👧‍👦 <b>/family</b> — Aadhar Family Search
🎮 <b>/ff</b> — Free Fire UID Lookup
🎮 <b>/bgmi</b> — BGMI UID Lookup
👻 <b>/snap</b> — Snapchat Username Lookup
🔍 <b>/deep</b> — Deep Lookup (Number → Aadhar → Family)

━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <i>Click any button below or use commands!</i>
━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Number", callback_data="number"),
            InlineKeyboardButton("🪪 Aadhar", callback_data="aadhar"),
        ],
        [
            InlineKeyboardButton("👨‍👩‍👧‍👦 Family", callback_data="family"),
            InlineKeyboardButton("🔍 Deep Lookup", callback_data="deep"),
        ],
        [
            InlineKeyboardButton("🎮 Free Fire", callback_data="ff"),
            InlineKeyboardButton("🎮 BGMI", callback_data="bgmi"),
        ],
        [
            InlineKeyboardButton("👻 Snapchat", callback_data="snap"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """
🆘 <b>HELP - Call OSINT Bot</b>

📱 <b>/number</b> <code>[mobile number]</code>
   Search any mobile number for details

🪪 <b>/aadhar</b> <code>[aadhar number]</code>
   Search Aadhar card details

👨‍👩‍👧‍👦 <b>/family</b> <code>[aadhar number]</code>
   Search family members via Aadhar

🎮 <b>/ff</b> <code>[uid]</code>
   Search Free Fire player info

🎮 <b>/bgmi</b> <code>[uid]</code>
   Search BGMI player info

👻 <b>/snap</b> <code>[username]</code>
   Search Snapchat profile info

🔍 <b>/deep</b> <code>[mobile number]</code>
   Deep lookup: Number → Aadhar → Family

💡 <i>You can also use the buttons from /start</i>
"""
    await update.message.reply_text(help_text, parse_mode="HTML")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    action = query.data
    user_id = query.from_user.id
    current_action[user_id] = action

    prompts = {
        "number": "📱 <b>Enter Mobile Number:</b>\n\n<i>Example: 9876543210</i>",
        "aadhar": "🪪 <b>Enter Aadhar Number:</b>\n\n<i>Example: 393933081942</i>",
        "family": "👨‍👩‍👧‍👦 <b>Enter Aadhar Number for Family Search:</b>\n\n<i>Example: 984154610245</i>",
        "ff": "🎮 <b>Enter Free Fire UID:</b>\n\n<i>Example: 123456789</i>",
        "bgmi": "🎮 <b>Enter BGMI UID:</b>\n\n<i>Example: 5121439477</i>",
        "snap": "👻 <b>Enter Snapchat Username:</b>\n\n<i>Example: priyapanchal272</i>",
        "deep": "🔍 <b>Enter Mobile Number for Deep Lookup:</b>\n\n<i>This will search: Number → Aadhar → Family</i>",
    }

    prompt = prompts.get(action, "Enter input:")
    await query.message.reply_text(prompt, parse_mode="HTML")
    return WAITING_INPUT


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct commands with arguments."""
    command = update.message.text.split()[0].replace("/", "").replace("@", "").split("@")[0]
    args = update.message.text.split()[1:] if len(update.message.text.split()) > 1 else []

    if not args:
        user_id = update.message.from_user.id
        current_action[user_id] = command
        prompts = {
            "number": "📱 <b>Enter Mobile Number:</b>",
            "aadhar": "🪪 <b>Enter Aadhar Number:</b>",
            "family": "👨‍👩‍👧‍👦 <b>Enter Aadhar Number:</b>",
            "ff": "🎮 <b>Enter Free Fire UID:</b>",
            "bgmi": "🎮 <b>Enter BGMI UID:</b>",
            "snap": "👻 <b>Enter Snapchat Username:</b>",
            "deep": "🔍 <b>Enter Mobile Number:</b>",
        }
        await update.message.reply_text(
            prompts.get(command, "Enter input:"), parse_mode="HTML"
        )
        return WAITING_INPUT

    input_text = args[0]
    await process_lookup(update, command, input_text)
    return ConversationHandler.END


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user text input after selecting an action."""
    user_id = update.message.from_user.id
    action = current_action.get(user_id)

    if not action:
        await update.message.reply_text(
            "⚠️ <b>Please select an option first!</b>\n\nUse /start to see available options.",
            parse_mode="HTML",
        )
        return ConversationHandler.END

    input_text = update.message.text.strip()
    await process_lookup(update, action, input_text)
    current_action.pop(user_id, None)
    return ConversationHandler.END


async def process_lookup(update: Update, action: str, input_text: str):
    """Process the lookup based on action type."""
    wait_msg = await update.message.reply_text("⏳ <b>Searching... Please wait!</b>", parse_mode="HTML")

    try:
        if action == "number":
            data = number_lookup(input_text)
            title = f"📱 Number Lookup — {input_text}"
        elif action == "aadhar":
            data = aadhar_lookup(input_text)
            title = f"🪪 Aadhar Lookup — {input_text}"
        elif action == "family":
            data = aadhar_family(input_text)
            title = f"👨‍👩‍👧‍👦 Family Search — {input_text}"
        elif action == "ff":
            data = freefire_lookup(input_text)
            title = f"🎮 Free Fire Lookup — {input_text}"
        elif action == "bgmi":
            data = bgmi_lookup(input_text)
            title = f"🎮 BGMI Lookup — {input_text}"
        elif action == "snap":
            data = snapchat_lookup(input_text)
            title = f"👻 Snapchat Lookup — {input_text}"
        elif action == "deep":
            result_text = await deep_lookup(input_text)
            await safe_send(update, result_text)
            # Send PDF
            await send_pdf(update, f"Deep Lookup — {input_text}", result_text)
            await wait_msg.delete()
            return
        else:
            await wait_msg.edit_text("❌ <b>Unknown action!</b>", parse_mode="HTML")
            return

        result_text = build_result_text(title, data)
        await safe_send(update, result_text)

        # Send PDF
        await send_pdf(update, title, result_text)
        await wait_msg.delete()

    except Exception as e:
        logger.error(f"Lookup error: {e}")
        error_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━
❌ <b>ERROR</b>
━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ <b>Error:</b> <code>{str(e)}</code>
🔄 <i>Please try again later</i>

━━━━━━━━━━━━━━━━━━━━━━━━━"""
        await wait_msg.edit_text(error_text, parse_mode="HTML")


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
            await update.message.reply_text(part, parse_mode="HTML")


async def send_pdf(update: Update, title: str, text: str):
    """Generate and send a PDF of the result."""
    try:
        pdf_path = generate_pdf(title, text)
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename=f"OSINT_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                caption="📄 <b>PDF Report Generated!</b>",
                parse_mode="HTML",
            )
        os.unlink(pdf_path)
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        await update.message.reply_text(
            f"⚠️ <i>PDF generation failed: {e}</i>", parse_mode="HTML"
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation."""
    user_id = update.message.from_user.id
    current_action.pop(user_id, None)
    await update.message.reply_text("❌ <b>Cancelled!</b>", parse_mode="HTML")
    return ConversationHandler.END


def run_bot():
    """Start the Telegram bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("number", handle_command),
            CommandHandler("aadhar", handle_command),
            CommandHandler("family", handle_command),
            CommandHandler("ff", handle_command),
            CommandHandler("bgmi", handle_command),
            CommandHandler("snap", handle_command),
            CommandHandler("deep", handle_command),
            CallbackQueryHandler(button_handler),
        ],
        states={
            WAITING_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)

    logger.info("🤖 Bot started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()
