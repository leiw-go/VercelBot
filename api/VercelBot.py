from flask import Flask, request, g
from telegram import Bot, Update
import leancloud
import os
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext, CommandHandler
from httpx import AsyncClient

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_ID = os.getenv('LEANCLOUD_APP_ID')
APP_KEY = os.getenv('LEANCLOUD_APP_KEY')

# 用你的bot token替换
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)
client = AsyncClient()

leancloud.init(APP_ID, APP_KEY)

# 用你的数据表名称替换
MyTable = leancloud.Object.extend('links')


def command_all(update: Update, context: CallbackContext):
    query = MyTable.query
    results = query.find()
    if results is None:
        bot.sendMessage(chat_id=update.effective_chat.id, text='links are empty, add your collected link')
    else:
        links = [row.get('link') for row in results]
        bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(links))
    return 'ok'


def message_group_link(update: Update, context):
    # 在这里处理接收到的消息
    chat_id = update.message.chat_id
    text = update.message.text
    if text == '/great':
        handle_great(update)
    elif text.startswith('http') or text.startswith('https'):
        handle_add_link(update)
    else:
        bot.sendMessage(chat_id=chat_id, text='Please send a valid command or link')
        bot.send_message(chat_id=chat_id, text=f"您发送了: {text}")


dispatcher.add_handler(CommandHandler('all', command_all))
dispatcher.add_handler(MessageHandler(Filters.text, message_group_link))


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"


@app.route('/', methods=['GET'])
def hello():
    return 'I am a Bot'


def handle_all(update: Update):
    chat_id = update.message.chat.id
    query = MyTable.query
    results = query.find()
    links = [row.get('link') for row in results]
    bot.sendMessage(chat_id=chat_id, text='\n'.join(links))
    return 'ok'


def handle_great(update: Update):
    chat_id = update.message.chat_id
    bot.sendMessage(chat_id=chat_id, text='Great girls adding ...')
    return 'ok'


def handle_add_link(update: Update):
    chat_id = update.message.chat_id
    text = update.message.text
    links = MyTable()
    links.set('links', text)
    links.save()
    bot.sendMessage(chat_id=chat_id, text='Girls link added')
