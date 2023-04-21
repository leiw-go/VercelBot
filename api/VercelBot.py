from flask import Flask, request
import telegram
import os

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# 用你的bot token替换
bot = telegram.Bot(token=BOT_TOKEN)


@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text
    bot.sendMessage(chat_id=chat_id, text=text)
    return 'ok'
