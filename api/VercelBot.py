from flask import Flask, request
from telegram import Bot, Update
import os
from telegram.ext import Dispatcher, MessageHandler, Filters
from httpx import AsyncClient

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')


# 用你的bot token替换
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)
client = AsyncClient(limits={"max_connections": 100})


def handle_message(update: Update, context):
    # 在这里处理接收到的消息
    chat_id = update.message.chat_id
    text = update.message.text
    bot.send_message(chat_id=chat_id, text=f"您发送了: {text}")


dispatcher.add_handler(MessageHandler(Filters.text, handle_message))


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"


@app.route('/', methods=['GET'])
def hello():
    return 'I am a Bot'
