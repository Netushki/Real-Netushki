import discord
import os
import random
from discord.ext import commands
from flask import Flask
import threading
import re

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Идентификатор сервера и каналов
GUILD_ID = 1185300118518378506  # Разрешённый сервер
COUNTING_CHANNEL_ID = 1344299177386967120  # Канал считалки
SCREENSHOT_CHANNEL_ID = 1344388680953106512  # Канал скриншотов

# Создаём объект для бота с необходимыми интентами
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Функция для поиска чисел в тексте
def find_numbers(text):
    return [int(num) for num in re.findall(r'\b\d+\b', text)]

# Бот выходит с чужих серверов
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id != GUILD_ID:
            print(f"Leaving unauthorized server: {guild.name} ({guild.id})")
            await guild.leave()
        else:
            print(f"Connected to {guild.name} ({guild.id})")

# Обработчик сообщений
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Проверка сообщений в канале считалки (можно текст, но обязательно число)
    if message.channel.id == COUNTING_CHANNEL_ID:
        if not find_numbers(message.content):
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"{message.author.mention}, твоё сообщение должно содержать число больше прошлого на 1!"
                )
                await warning.delete(delay=3)
            except discord.Forbidden:
                print("Не удалось удалить сообщение (нет прав).")
            return

    # Проверка сообщений в канале для скриншотов (только вложения, без текста)
    if message.channel.id == SCREENSHOT_CHANNEL_ID:
        if not message.attachments or message.content.strip():
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"{message.author.mention}, в этом канале можно отправлять только скриншот прошлого сообщения без своего текста!"
                )
                await warning.delete(delay=3)
            except discord.Forbidden:
                print("Не удалось удалить сообщение (нет прав).")
            return

    await bot.process_commands(message)

# Запуск Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

bot.run(TOKEN)



