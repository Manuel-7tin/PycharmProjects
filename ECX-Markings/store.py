def chidinma():
    # Ogbuanya Chidinma Daniella
    # Telegram Game Playing Bot

    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
    import random

    TOKEN = "7243310390:AAEkJIcDp3Ux-20xwzyJv7ba65JV72DVhvE"

    games = {}

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

        await update.message.reply_text(
            "Welcome to the Game Bot! Choose a game:\n"
            "1. /guess_number\n"
            "2. /tic_tac_toe\n"
            "3. /rock_paper_scissors"
        )

    async def guess_number(update: Update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.message.chat_id
        number = random.randint(1, 10)
        games[chat_id] = number
        await update.message.reply_text("I have picked a number between 1 and 10. Try to guess it!")

    async def check_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.message.chat_id
        guess = int(update.message.text)
        if chat_id in games:
            if guess == games[chat_id]:
                await update.message.reply_text("🎉 Correct! You guessed the number!")
                del games[chat_id]
            else:
                await update.message.reply_text("❌ Wrong! Try again.")

    async def tic_tac_toe(update: Update, context: ContextTypes.DEFAULT_TYPE):

        keyboard = [[InlineKeyboardButton("Play Tic-Tac-Toe", callback_data="tic_tac_toe_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Click to start Tic-Tac-Toe!", reply_markup=reply_markup)

    async def tic_tac_toe_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="Tic-Tac-Toe is under construction! 😅")

    async def rock_paper_scissors(update: Update, context: ContextTypes.DEFAULT_TYPE):

        keyboard = [
            [InlineKeyboardButton("Rock", callback_data="rps_rock"),
             InlineKeyboardButton("Paper", callback_data="rps_paper"),
             InlineKeyboardButton("Scissors", callback_data="rps_scissors")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose Rock, Paper, or Scissors:", reply_markup=reply_markup)

    async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        user_choice = query.data.split("_")[1]
        bot_choice = random.choice(["rock", "paper", "scissors"])
        result = determine_rps_winner(user_choice, bot_choice)
        await query.answer()
        await query.edit_message_text(f"You chose {user_choice}. I chose {bot_choice}. {result}")

    def determine_rps_winner(user, bot):
        if user == bot:
            return "It's a tie! 🤝"
        if (user == "rock" and bot == "scissors") or (user == "paper" and bot == "rock") or (
                user == "scissors" and bot == "paper"):
            return "🎉 You win!"
        return "😢 I win!"

    def main():
        print("In main")
        app = Application.builder().token(TOKEN).build()
        print("in first build")

        app = Application.builder().token(TOKEN).build()  # ✅ Correct
        print("in second build")

        app = Application.builder().token(TOKEN).build()  # ✅ CORRECT
        print("in third build")

        app.add_handler(CommandHandler("start", start))
        print("After adding first hnadler")

        app.add_handler(CommandHandler("guess_number", guess_number))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_guess))
        app.add_handler(CommandHandler("tic_tac_toe", tic_tac_toe))
        app.add_handler(CallbackQueryHandler(tic_tac_toe_game, pattern="tic_tac_toe_start"))
        app.add_handler(CommandHandler("rock_paper_scissors", rock_paper_scissors))
        app.add_handler(CallbackQueryHandler(rps_game, pattern="rps_.*"))
        print("After adding all handlers")

        app.run_polling()
        print("After running polling")

        Update.idle()
        print("After calling idle")

    if __name__ == "__main__":
        main()