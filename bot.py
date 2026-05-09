"""
Telegram Channel Management Bot powered by Groq AI
====================================================
Helps channel members find tutorials, resources, and get answers.

Requirements:
    pip install python-telegram-bot groq python-dotenv

Setup:
    1. Copy .env.example to .env and fill in your tokens
    2. Run: python bot.py
"""

import logging
import os
from dotenv import load_dotenv
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
CHANNEL_NAME   = os.getenv("CHANNEL_NAME", "Our Channel")

import httpx
groq_client = Groq(
    api_key=GROQ_API_KEY,
    http_client=httpx.Client()
)

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are a helpful AI assistant managing the Telegram channel "{CHANNEL_NAME}".

Your job is to:
- Help members find tutorials, guides, and learning resources
- Answer questions clearly and concisely
- Suggest step-by-step instructions when members need to do something
- Recommend relevant topics or categories when relevant
- Be friendly, supportive, and encouraging

Guidelines:
- Keep responses concise (under 400 words unless a detailed explanation is truly needed)
- Use bullet points or numbered steps for clarity
- If you don't know something specific to the channel, say so honestly
- Always end with an offer to help further or ask if the member needs more detail
- Use plain text only (no markdown bold/italic — Telegram handles its own formatting)
"""

# ── Per-user conversation history (in-memory) ─────────────────────────────────
conversation_history: dict[int, list[dict]] = {}

MAX_HISTORY = 10  # messages to retain per user


def get_ai_response(user_id: int, user_message: str) -> str:
    """Send message to Groq and return the AI reply."""
    history = conversation_history.setdefault(user_id, [])

    history.append({"role": "user", "content": user_message})

    # Trim to last MAX_HISTORY messages
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=600,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"Groq API error: {type(e).__name__}: {e}")
        return f"DEBUG ERROR: {type(e).__name__}: {str(e)[:200]}"


# ── Command handlers ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message with quick-action buttons."""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("📚 Find Tutorials",    callback_data="tutorials"),
            InlineKeyboardButton("🛠️ How To Guides",    callback_data="howto"),
        ],
        [
            InlineKeyboardButton("❓ Ask a Question",    callback_data="ask"),
            InlineKeyboardButton("📋 Channel Topics",   callback_data="topics"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Welcome to {CHANNEL_NAME}, {user.first_name}!\n\n"
        "I'm your AI assistant. I can help you:\n"
        "• Find tutorials and learning resources\n"
        "• Walk you through how to do things step-by-step\n"
        "• Answer questions about channel topics\n\n"
        "Just type your question, or tap a button below to get started!",
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands."""
    await update.message.reply_text(
        "🤖 Here's what I can do:\n\n"
        "/start    — Welcome menu with quick actions\n"
        "/find     — Search for a tutorial (e.g. /find Python basics)\n"
        "/howto    — Get step-by-step instructions (e.g. /howto install Docker)\n"
        "/topics   — Browse channel topics\n"
        "/reset    — Clear conversation history\n\n"
        "Or just type any question and I'll answer it directly!"
    )


async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search for tutorials: /find <topic>"""
    if not context.args:
        await update.message.reply_text(
            "Please tell me what to find!\n"
            "Example: /find Python for beginners"
        )
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching for: {query}...")

    prompt = (
        f"The user wants to find tutorials or resources about: '{query}'.\n"
        "Provide 3–5 specific suggestions with a brief description of each. "
        "Include beginner, intermediate, and advanced options if applicable."
    )
    reply = get_ai_response(update.effective_user.id, prompt)
    await update.message.reply_text(reply)


async def howto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Step-by-step guide: /howto <task>"""
    if not context.args:
        await update.message.reply_text(
            "Tell me what you need to do!\n"
            "Example: /howto set up a virtual environment in Python"
        )
        return

    task = " ".join(context.args)
    await update.message.reply_text(f"🛠️ Getting steps for: {task}...")

    prompt = (
        f"Give a clear, numbered step-by-step guide on how to: '{task}'.\n"
        "Keep each step short and actionable. Include any prerequisites at the top."
    )
    reply = get_ai_response(update.effective_user.id, prompt)
    await update.message.reply_text(reply)


async def topics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show channel topics."""
    prompt = (
        "List the main topics and categories that a helpful tech/learning Telegram channel "
        "would cover. Group them into 4–6 categories with 3–4 sub-topics each."
    )
    reply = get_ai_response(update.effective_user.id, prompt)
    await update.message.reply_text(f"📋 Channel Topics\n\n{reply}")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear user's conversation history."""
    user_id = update.effective_user.id
    conversation_history.pop(user_id, None)
    await update.message.reply_text(
        "🔄 Conversation cleared! Starting fresh. How can I help you?"
    )


# ── Inline button callbacks ────────────────────────────────────────────────────

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data    = query.data

    responses = {
        "tutorials": (
            "What topic would you like tutorials for? "
            "Just type it and I'll find great resources!\n\n"
            "Examples: Python, web development, machine learning, Docker, React..."
        ),
        "howto": (
            "What do you need help doing? Type it and I'll give you step-by-step instructions!\n\n"
            "Examples: install Node.js, create a REST API, deploy to Heroku..."
        ),
        "ask": (
            "Go ahead and ask me anything! I'll do my best to help you out."
        ),
        "topics": None,  # handled below with AI
    }

    if data == "topics":
        prompt = (
            "List the most popular learning topics for a tech channel. "
            "Use emojis and short descriptions. Group into 5 categories."
        )
        reply = get_ai_response(user_id, prompt)
        await query.edit_message_text(f"📋 Popular Topics\n\n{reply}")
    else:
        await query.edit_message_text(responses[data])


# ── Free-text message handler ──────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any plain text message with Groq AI."""
    user_message = update.message.text
    user_id      = update.effective_user.id

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    reply = get_ai_response(user_id, user_message)
    await update.message.reply_text(reply)


# ── App entry point ────────────────────────────────────────────────────────────

def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_command))
    app.add_handler(CommandHandler("find",   find_command))
    app.add_handler(CommandHandler("howto",  howto_command))
    app.add_handler(CommandHandler("topics", topics_command))
    app.add_handler(CommandHandler("reset",  reset_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"Bot started for channel: {CHANNEL_NAME}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
    
