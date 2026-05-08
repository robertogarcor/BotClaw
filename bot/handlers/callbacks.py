from telegram import Update
from telegram.ext import ContextTypes


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "new_session":
        from bot.handlers.commands import new_command
        await new_command(update, context)
    elif data == "status":
        from bot.handlers.commands import status_command
        await status_command(update, context)
    elif data == "help":
        from bot.handlers.commands import help_command
        await help_command(update, context)