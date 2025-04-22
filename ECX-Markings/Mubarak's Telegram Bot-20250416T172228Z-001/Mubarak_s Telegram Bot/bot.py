import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from games import number_guessing, tic_tac_toe, rock_paper_scissors

# Enable logging to track bot activity
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start command - Welcome message with available games
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Welcome to the Telegram Game Bot!\nChoose a game to play:\n"
        "/guess - Number Guessing Game 🔢\n"
        "/tictactoe - Tic-Tac-Toe ❌⭕\n"
        "/rps - Rock-Paper-Scissors ✊✋✌️"
    )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")

def main():
    # Load environment variables
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        raise ValueError("Bot token not found! Check .env file.")

    # Create application and add handlers
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("guess", number_guessing.play))
    application.add_handler(CommandHandler("tictactoe", tic_tac_toe.play))
    application.add_handler(CommandHandler("rps", rock_paper_scissors.play))

    # Add message handlers for game inputs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, number_guessing.guess))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tic_tac_toe.handle_tictactoe_move))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rock_paper_scissors.rps_choice))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()