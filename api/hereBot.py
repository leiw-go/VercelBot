import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = '6028082352:AAFBjghqv3Lzh6r-s51VT4ET9m5UhM2tCbY'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

app = ApplicationBuilder().token(BOT_TOKEN).build()

start_handler = CommandHandler('start', start)
app.add_handler(start_handler)

app.run_polling()
