from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from common import create_short_url, short_url_to_long, get_all_urls, redirect_count
import asyncio

bot = AsyncTeleBot('')


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """
            Commands:
            /start
            /help
            /create <your url> (/create https://google.com)
            /show_url (Shows all of your url`s)
            /redirects (counts all redirects from links)
    """)


@bot.message_handler(commands=['create'])
async def create_message(message: Message):
    long_url = message.text.replace('/create', '')
    short_url = await create_short_url(long_url, user_id=message.from_user.id)
    await bot.reply_to(message, short_url)


@bot.message_handler(commands=['show_url'])
async def show_all_url(message: Message):
    result = await get_all_urls(message.from_user.id)
    list_of_text_links = [f'{data["short_url"]} -> {data["long_url"]}' async for data in result]
    await bot.send_message(message.chat.id, '\r\n'.join(list_of_text_links) if list_of_text_links else 'Nothing')


@bot.message_handler(commands=['redirects'])
async def redirects(message: Message):
    link_count_redirects = await redirect_count(message.from_user.id)
    list_data = []
    async for data in link_count_redirects:
        list_data.append(f"links: {data['_id']}: redirect count: {data['links_count']}")
    await bot.send_message(message.chat.id, '\r\n'.join(list_data) if list_data else 'Nothing')


@bot.message_handler(func=lambda message: True)
async def returning_message(message: Message):
    long_url = await short_url_to_long(message.text)
    await bot.reply_to(message, long_url)


asyncio.run(bot.polling())
