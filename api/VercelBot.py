from flask import Flask, request
import telegram
import os

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# 用你的bot token替换
bot = telegram.Bot(token=BOT_TOKEN)


@app.route('/webhook', methods=['POST'])
async def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text
    await bot.sendMessage(chat_id=chat_id, text=text)
    return 'ok'


@app.route('/', methods=['GET'])
def hello():
    return 'I am a Bot'
