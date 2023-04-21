from flask import Flask, request, g
from telegram import Bot, Update
import mysql.connector
import os
from telegram.ext import Dispatcher, MessageHandler, Filters
from httpx import AsyncClient

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWD = os.getenv('DB_PASSWD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# 用你的bot token替换
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)
client = AsyncClient()

DATABASE_CONFIG = {
    'user': DB_USERNAME,
    'password': DB_PASSWD,
    'host': DB_HOST,
    'database': DB_NAME
}


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(**DATABASE_CONFIG)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def handle_message(update: Update, context):
    # 在这里处理接收到的消息
    chat_id = update.message.chat_id
    text = update.message.text
    if text == '/all':
        handle_all(update)
    elif text == '/great':
        handle_great(update)
    elif text.startswith('http') or text.startswith('https'):
        handle_add_link(update)
    else:
        bot.sendMessage(chat_id=chat_id, text='Please send a valid command or link')
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


def handle_all(update: Update):
    chat_id = update.message.chat.id
    cur = get_db().cursor()
    cur.execute('SELECT link FROM links')
    results = cur.fetchall()
    links = [row[0] for row in results]
    bot.sendMessage(chat_id=chat_id, text='\n'.join(links))
    return 'ok'


def handle_great(update: Update):
    chat_id = update.message.chat_id
    text = update.message.text
    bot.sendMessage(chat_id=chat_id, text='Great girls adding ...')
    return 'ok'


def handle_add_link(update: Update):
    chat_id = update.message.chat_id
    text = update.message.text
    db = get_db()
    cur = db.cursor()
    cur.execute('INSERT INTO links (link) VALUES (%s)', (text,))
    db.commit()
    bot.sendMessage(chat_id=chat_id, text='Girls link added')
