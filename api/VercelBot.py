import os
import requests
import leancloud
from typing import List
from telegram import Update, Bot
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, MessageHandler
from telegram.ext import filters
from telegram.ext.filters import MessageFilter
import httpx
from flask import Flask, request

# 定义常量
BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_ID = os.getenv('LEANCLOUD_APP_ID')
APP_KEY = os.getenv('LEANCLOUD_APP_KEY')

# 初始化
app = Flask(__name__)
leancloud.init(APP_ID, APP_KEY)

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, workers=0)

# 用你的数据表名称替换
linksTable = leancloud.Object.extend('links')
videosTable = leancloud.Object.extend('videos')


async def command_start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot to make you happy")
    return 'ok'


async def command_all(update: Update, context: CallbackContext):
    query = linksTable.query
    results = query.find()
    if results is None:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text='links are empty, add your collected link')
    else:
        links = [row.get('link') for row in results]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(links))
    return 'ok'


async def command_show(update: Update, context: CallbackContext):
    query = videosTable.query
    results = query.find()
    if results is None:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text='videos are empty, add your collected link')
    else:
        files = [row.get('file_id') for row in results]
        urls = []
        await getUrl(files, urls)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(urls))
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='All girl shows here')
    return 'ok'


async def command_great(update: Update, context: CallbackContext):
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text='Great girls adding ...')
    return 'ok'


async def message_group_link(update: Update, context: CallbackContext):
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


async def getUrl(files: List[str], urls: List[str]) -> List[str]:
    async with httpx.AsyncClient() as client:
        for fileId in files:
            response = await client.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={fileId}")
            file_path = response.json()["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            urls.append(file_url)
    return urls


# dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
dispatcher.add_handler(CommandHandler("start", command_start))
dispatcher.add_handler(CommandHandler("groups", command_all))
dispatcher.add_handler(CommandHandler("show", command_show))
dispatcher.add_handler(CommandHandler("great", command_great))
dispatcher.add_handler(MessageHandler(FilterAwesome(), message_group_link))
# dispatcher.add_handler(MessageHandler(filters.FORWARDED & filters.VIDEO, message_great_video))
dispatcher.add_handler(MessageHandler(filters.Filters.video, message_great_video))


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), Bot(BOT_TOKEN))
    dispatcher.process_update(update)
    return 'ok'


@app.route('/', methods=['GET'])
def hello():
    return 'I am a develop Bot. Coding ...'
