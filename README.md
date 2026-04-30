# 🔒 Call OSINT — Auto OSINT Lookup Bot & Website

> Telegram Bot + Web Dashboard — Sirf ek input daalo, baaki sab automatic!

---

## 🔥 How It Works

**Koi command ki zaroorat nahi!** Bot khud detect karta hai:

| Input Type | Example | Auto Action |
|-----------|---------|-------------|
| 📱 10-digit number | `9876543210` | Number → Aadhar → Family (full chain) |
| 🪪 12-digit number | `393933081942` | Aadhar → Family → Numbers (full chain) |
| 🎮 7-9 digit number | `123456789` | Free Fire UID Lookup |
| 🎯 10+ digits (non-mobile) | `5121439477` | BGMI UID Lookup |
| 👻 Text/username | `priyapanchal272` | Snapchat Lookup |

**Har result ka PDF auto-download milta hai!**

---

## 🛡️ Features

- ⚡ **Auto-Detect** — Input type auto pehchaan ta hai
- 🔗 **Auto-Chain** — Mobile se Aadhar, Aadhar se Family sab auto
- 📄 **PDF Reports** — Har result ka PDF bot mein milega
- 🎨 **Emoji Decorated** — Beautiful formatted results
- 🌐 **Web Dashboard** — Dark themed website
- 🤖 **Telegram Bot** — Inline buttons + auto mode

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/Aman262626/Call-osint.git
cd Call-osint
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python main.py
```

Bot + Website dono start ho jayenge!

---

## 🌐 Render Pe Free Deploy

### Step-by-step:

1. **[render.com](https://dashboard.render.com)** pe jao — Sign up/Login

2. **New → Web Service** click karo

3. **GitHub repo connect karo:** `Aman262626/Call-osint`

4. **Settings fill karo:**
   - **Name:** `call-osint`
   - **Branch:** `base-branch`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Plan:** `Free`

5. **Environment Variables add karo:**

   | Key | Value |
   |-----|-------|
   | `BOT_TOKEN` | `8491544250:AAEUCsJ_lT_2oNQWq4CcI0b2-x6g2h_2DvM` |
   | `ADMIN_ID` | `5451167865` |
   | `API_KEY` | `ft-key-tr-jzynhifn87aq` |
   | `PORT` | `5000` |

6. **"Create Web Service"** click karo

7. Wait for build — Site live hogi at `https://call-osint.onrender.com`

---

## 📁 Project Structure

```
Call-osint/
├── main.py              # Entry point (bot + web)
├── bot.py               # Telegram bot (auto-detect mode)
├── app.py               # Flask web server
├── api_client.py        # OSINT API wrapper
├── config.py            # Configuration
├── pdf_generator.py     # PDF report generator
├── requirements.txt     # Dependencies
├── render.yaml          # Render blueprint (free plan)
├── templates/
│   └── index.html       # Web dashboard
└── static/
    └── style.css        # Styles
```

---

## ⚙️ Tech Stack

- **Python 3.11** — Runtime
- **python-telegram-bot** — Bot API
- **Flask** — Web framework
- **FPDF2** — PDF generation
- **Render** — Free hosting

---

## 📄 License

MIT License
