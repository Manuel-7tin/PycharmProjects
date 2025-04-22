import random
from telegram import Update
from telegram.ext import CallbackContext

CHOICES = ["rock", "paper", "scissors"]

async def play(update: Update, context: CallbackContext):
    context.user_data["playing_rps"] = True  # Set game state
    await update.message.reply_text("Choose: rock, paper, or scissors.")

async def rps_choice(update: Update, context: CallbackContext):
    if not context.user_data.get("playing_rps"):
        await update.message.reply_text("Start a game first with /rps.")
        return

    user_choice = update.message.text.lower()
    if user_choice not in CHOICES:
        await update.message.reply_text(
            "Invalid choice! Choose rock, paper, or scissors."
        )
        return

    bot_choice = random.choice(CHOICES)
    result = determine_winner(user_choice, bot_choice)
    await update.message.reply_text(f"I chose {bot_choice}. {result}")
    context.user_data["playing_rps"] = False  # End game state

def determine_winner(user, bot):
    if user == bot:
        return "It's a tie!"
    if (user == "rock" and bot == "scissors") or \
       (user == "scissors" and bot == "paper") or \
       (user == "paper" and bot == "rock"):
        return "You win!"
    return "I win!"