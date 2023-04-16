# -*- coding: utf-8 -*-
from flask import Flask, request
import telegram
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 设置 Telegram Bot Token 和 Webhook URL
BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


# 初始化 Flask 应用程序
app = Flask(__name__)

# 初始化 Telegram Bot
bot = telegram.Bot(token=BOT_TOKEN)


# 定义 Webhook 响应函数
@app.route('/{}'.format(BOT_TOKEN), methods=['POST'])
def respond():
    # 获取请求中的消息
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # 处理消息
    if update is None:
        bot.sendMessage(chat_id=0000, text='wrong message')
    else:
        text = update.message.text
        chat_id = update.message.chat_id
        bot.sendMessage(chat_id=chat_id, text=text)

    return 'ok'


@app.route('/welcome/{}'.format(BOT_TOKEN), methods=['POST'])
def getToken():
    return BOT_TOKEN


@app.route('/')
def welcome():
    return 'Hello, I am a Bot'


# 设置 Webhook
async def set_webhook():
    await bot.setWebhook(url=WEBHOOK_URL)


application = ApplicationBuilder().token('BOT_TOKEN').build()

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

application.run_webhook(
    listen='0.0.0.0',
    port=443,
    webhook_url='https://boyduty.club:443'
)