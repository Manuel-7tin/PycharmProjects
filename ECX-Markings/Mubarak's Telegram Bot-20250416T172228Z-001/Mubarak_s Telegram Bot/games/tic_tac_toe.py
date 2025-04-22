import random
from telegram import Update
from telegram.ext import CallbackContext

# Dictionary to store active Tic-Tac-Toe games
active_games = {}

# Function to format and display the Tic-Tac-Toe board
def format_board(board):
    return f"\n{board[0]} | {board[1]} | {board[2]}\n" \
        f"---------\n" \
        f"{board[3]} | {board[4]} | {board[5]}\n" \
        f"---------\n" \
        f"{board[6]} | {board[7]} | {board[8]}\n"

# Function to check for a winner
def check_winner(board, player):
    win_patterns = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
                    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
                    (0, 4, 8), (2, 4, 6)]  # Diagonals
    return any(board[a] == board[b] == board[c] == player for a, b, c in win_patterns)

# Start a new Tic-Tac-Toe game
async def play(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if user_id in active_games:
        await update.message.reply_text(
            "You're already playing! Send a number (1-9) to make a move."
        )
        return

    board = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    active_games[user_id] = board

    await update.message.reply_text(
        f"Tic-Tac-Toe started!\nYou are 'X'. Send a number (1-9) to make a move.\n{format_board(board)}"
    )

# Handle user moves
async def handle_tictactoe_move(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if user_id not in active_games:
        return

    board = active_games[user_id]
    move = update.message.text.strip()

    # Validate user move
    if move not in [str(i) for i in range(1, 10)] or board[int(move)-1] in ["X", "O"]:
        await update.message.reply_text(
            "Invalid move! Choose an available number (1-9)."
        )
        return

    # Player's move
    board[int(move)-1] = "X"

    # Check if player won
    if check_winner(board, "X"):
        await update.message.reply_text(f"You win!\n{format_board(board)}")
        del active_games[user_id]
        return

    # Check for a draw
    if all(cell in ["X", "O"] for cell in board):
        await update.message.reply_text(f"It's a draw!\n{format_board(board)}")
        del active_games[user_id]
        return

    # Bot's move
    available_moves = [i for i in range(9) if board[i] not in ["X", "O"]]
    bot_move = random.choice(available_moves)
    board[bot_move] = "O"

    # Check if bot won
    if check_winner(board, "O"):
        await update.message.reply_text(f"Bot wins!\n{format_board(board)}")
        del active_games[user_id]
        return

    # Send updated board
    await update.message.reply_text(
        f"Your move:\n{format_board(board)}\nYour turn! Send a number (1-9)."
    )