import os
import requests
import leancloud
from telegram import Update, Bot
from telegram.ext import *
from telegram.ext.filters import MessageFilter
from httpx import AsyncClient
from flask import Flask, request

# 定义常量
BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_ID = os.getenv('LEANCLOUD_APP_ID')
APP_KEY = os.getenv('LEANCLOUD_APP_KEY')

# 初始化
app = Flask(__name__)
leancloud.init(APP_ID, APP_KEY)
client = AsyncClient()
application = ApplicationBuilder().token(BOT_TOKEN).build()
urls = []

# bot = Bot(token=BOT_TOKEN)
# dispatcher = Dispatcher(bot, None, workers=0)

# 用你的数据表名称替换
linksTable = leancloud.Object.extend('links')
videosTable = leancloud.Object.extend('videos')


async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot to make you happy")
    return 'ok'


async def command_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = linksTable.query
    results = query.find()
    if results is None:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text='links are empty, add your collected link')
    else:
        links = [row.get('link') for row in results]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(links))
    return 'ok'


async def command_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = videosTable.query
    results = query.find()
    if results is None:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text='videos are empty, add your collected link')
    else:
        files = [row.get('file_id') for row in results]
        getUrl(files)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(urls))
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='All girl shows here')
    return 'ok'


async def command_great(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='Great girls adding ...')
    return 'ok'


async def message_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 在这里处理接收到的消息
    text = update.message.text
    links = linksTable()
    links.set('link', text)
    links.save()
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='Girls link added')
    return 'ok'


async def message_great_video(update: Update, context: CallbackContext):
    # 在这里处理接收到的video
    video = update.message.video
    file_id = video.file_id
    videos = videosTable()
    videos.set('file_id', file_id)
    videos.save()
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='thinks for your video')
    return 'ok'


class FilterAwesome(MessageFilter):
    def filter(self, message):
        return message.text.startswith('http') or message.text.startswith('https')


def getUrl(files) -> urls:
    for fileId in files:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={fileId}")
        file_path = response.json()["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        urls.append(file_url)
    return urls


# dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
application.add_handler(CommandHandler("start", command_start))
application.add_handler(CommandHandler("groups", command_all))
application.add_handler(CommandHandler("show", command_show))
application.add_handler(CommandHandler("great", command_great))
application.add_handler(MessageHandler(FilterAwesome(), message_group_link))
# application.add_handler(MessageHandler(filters.FORWARDED & filters.VIDEO, message_great_video))
application.add_handler(MessageHandler(filters.VIDEO, message_great_video))


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), Bot(BOT_TOKEN))
    application.process_update(update)
    return "ok"


@app.route('/', methods=['GET'])
def hello():
    return 'I am a develop Bot. Coding ...'
