# 🔒 Call OSINT — Advanced OSINT Lookup Bot & Website

> Telegram Bot + Web Dashboard for OSINT lookups — Number, Aadhar, Family, Free Fire, BGMI, Snapchat

---

## 🛡️ Features

| Feature | Description |
|---------|-------------|
| 📱 **Number Lookup** | Mobile number details, operator, location |
| 🪪 **Aadhar Lookup** | Aadhar card information search |
| 👨‍👩‍👧‍👦 **Family Search** | Find family members via Aadhar |
| 🎮 **Free Fire** | Free Fire player UID lookup |
| 🎯 **BGMI** | BGMI player UID lookup |
| 👻 **Snapchat** | Snapchat profile details |
| 🔍 **Deep Lookup** | Number → Aadhar → Family (auto chain) |
| 📄 **PDF Reports** | Download results as PDF |
| 🌐 **Web Dashboard** | Beautiful dark-themed website |
| 🤖 **Telegram Bot** | Interactive bot with inline buttons |

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Aman262626/Call-osint.git
cd Call-osint
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables (optional)

```bash
export BOT_TOKEN="your-telegram-bot-token"
export ADMIN_ID="your-telegram-id"
export API_KEY="your-osint-api-key"
export PORT=5000
```

### 4. Run

```bash
python main.py
```

This starts both the **Telegram bot** and the **web server** on port 5000.

---

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu with buttons |
| `/help` | Show all commands |
| `/number <num>` | Number lookup |
| `/aadhar <num>` | Aadhar lookup |
| `/family <num>` | Aadhar family search |
| `/ff <uid>` | Free Fire lookup |
| `/bgmi <uid>` | BGMI lookup |
| `/snap <username>` | Snapchat lookup |
| `/deep <num>` | Deep lookup (Number → Aadhar → Family) |

---

## 🌐 Deploy on Render

### Step-by-step:

1. **Push to GitHub** (this repo)

2. **Go to [Render Dashboard](https://dashboard.render.com)**

3. **New → Web Service**

4. **Connect your GitHub repo** `Aman262626/Call-osint`

5. **Settings:**
   - **Name:** `call-osint`
   - **Runtime:** `Docker`
   - **Plan:** Free

6. **Environment Variables:**
   | Key | Value |
   |-----|-------|
   | `BOT_TOKEN` | Your Telegram bot token |
   | `ADMIN_ID` | Your Telegram user ID |
   | `API_KEY` | Your OSINT API key |
   | `PORT` | `5000` |

7. **Click "Create Web Service"**

8. Wait for deployment — your site will be live at `https://call-osint.onrender.com`

---

## 📁 Project Structure

```
Call-osint/
├── main.py              # Entry point (runs bot + web)
├── bot.py               # Telegram bot
├── app.py               # Flask web server
├── api_client.py        # OSINT API wrapper
├── config.py            # Configuration
├── pdf_generator.py     # PDF report generator
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker config for Render
├── render.yaml          # Render blueprint
├── templates/
│   └── index.html       # Web dashboard
└── static/
    └── style.css        # Website styles
```

---

## 📸 Screenshots

### Telegram Bot
- Beautiful emoji-decorated responses
- Inline keyboard buttons
- PDF report download

### Web Dashboard
- Dark theme with gradient animations
- Real-time API lookups
- Mobile responsive

---

## ⚙️ Tech Stack

- **Python 3.11**
- **python-telegram-bot** — Telegram Bot API
- **Flask** — Web framework
- **FPDF2** — PDF generation
- **Requests** — HTTP client
- **Gunicorn** — Production WSGI server

---

## 📄 License

MIT License — Use freely!
