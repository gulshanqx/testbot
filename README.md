# 🤖 Telegram AI Channel Management Bot (Groq-powered)

An AI assistant bot for your Telegram channel that helps members find tutorials,
get step-by-step guides, and ask questions — powered by Groq's ultra-fast LLaMA 3.

---

## ✨ Features

| Feature | Command | Description |
|--------|---------|-------------|
| Welcome menu | `/start` | Interactive buttons to get started |
| Find tutorials | `/find <topic>` | AI finds relevant learning resources |
| How-to guides | `/howto <task>` | Step-by-step instructions for any task |
| Browse topics | `/topics` | AI lists channel categories |
| Free chat | Just type! | Ask anything in plain text |
| Reset memory | `/reset` | Clear conversation history |

---

## 🚀 Setup (5 minutes)

### 1. Get your Telegram Bot Token
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the token it gives you

### 2. Get your Groq API Key
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up / log in
3. Go to **API Keys** → **Create new key**
4. Copy the key

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Open .env and fill in your tokens
```

Your `.env` should look like:
```
TELEGRAM_BOT_TOKEN=7123456789:AAF...
GROQ_API_KEY=gsk_...
CHANNEL_NAME=My Learning Channel
```

### 5. Run the bot
```bash
python bot.py
```

That's it! Go to Telegram, find your bot by its username, and send `/start`.

---

## 🔧 Customization

### Change the AI model
In `bot.py`, find `model="llama3-70b-8192"` and replace with:
- `llama3-8b-8192` — faster, lighter
- `mixtral-8x7b-32768` — larger context window
- `gemma2-9b-it` — Google's Gemma 2

### Customize the AI personality
Edit the `SYSTEM_PROMPT` variable in `bot.py` to match your channel's topic and tone.

### Add channel-specific resources
You can extend the system prompt with a list of your own tutorials or links:
```python
SYSTEM_PROMPT = """...
Our channel resources:
- Python basics: https://...
- Docker guide: https://...
"""
```

---

## 📁 File Structure
```
telegram_ai_bot/
├── bot.py           # Main bot code
├── requirements.txt # Python dependencies
├── .env.example     # Environment variable template
└── README.md        # This file
```

---

## 💡 Tips

- **Add to a group**: Make the bot an admin of your channel or group so it can read messages
- **Privacy mode**: For groups, disable privacy mode in @BotFather so the bot sees all messages
- **Keep it running**: Use a VPS, Railway, Render, or a Raspberry Pi to run it 24/7
- **Rate limits**: Groq's free tier is generous — more than enough for a channel bot

---

## 🛠️ Deployment (Optional)

### Run as a background service (Linux)
```bash
nohup python bot.py > bot.log 2>&1 &
```

### Deploy to Railway (free)
1. Push code to GitHub
2. Connect repo at [railway.app](https://railway.app)
3. Add environment variables in Railway dashboard
4. Deploy!
