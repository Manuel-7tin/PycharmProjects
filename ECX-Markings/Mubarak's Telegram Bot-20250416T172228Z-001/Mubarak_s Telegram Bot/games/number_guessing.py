#salaudeen mubarak onoruoiza
import random
from telegram import Update
from telegram.ext import CallbackContext

async def play(update: Update, context: CallbackContext):
    number = random.randint(1, 10)  # Choose a random number
    context.user_data["target"] = number  # Store the number for the user
    await update.message.reply_text("I have chosen a number between 1 and 10. Try to guess!")

async def guess(update: Update, context: CallbackContext):
    try:
        user_guess = int(update.message.text)  # Get the user's guess
    except ValueError:
        await update.message.reply_text("Please enter a valid number!")
        return

    target = context.user_data.get("target", None)  # Retrieve the stored number

    if target is None:
        await update.message.reply_text("Start the game first with /guess")
        return

    if user_guess == target:
        await update.message.reply_text("Correct! You guessed it!")
        del context.user_data["target"]  # Reset the game
    elif user_guess < target:
        await update.message.reply_text("Too low! Try again.")
    else:
        await update.message.reply_text("Too high! Try again.")