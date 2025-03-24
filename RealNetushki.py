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
GUILD_ID = 1185300118518378506  # Target server ID
COUNTING_CHANNEL_ID = 1344299177386967120  # Канал считалки
SCREENSHOT_CHANNEL_ID = 1344388680953106512  # Канал скриншотов

# Создаем объект для бота с необходимыми интентами
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Включаем доступ к содержимому сообщений
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Список URL для GIF
gif_urls = [
    "https://cdn.discordapp.com/attachments/1346943612373569557/1347573414142939279/attachment.gif",
    "https://cdn.discordapp.com/attachments/1322781202851041358/1347037669388980274/attachment.gif",
    "https://cdn.discordapp.com/attachments/1309799105756790794/1309909672446398534/speechmemified_Half_Life_Deathmatch_Source.jpg.gif",
    "https://tenor.com/view/speech-bubble-gif-26412022",
]

# Функция для поиска чисел в тексте
def find_numbers(text):
    return [int(num) for num in re.findall(r'\b\d+\b', text)]  # Ищет все числа в тексте

# Событие, когда бот подключается
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        print(f'Successfully connected to {guild.name} ({guild.id})')
    else:
        print(f"Bot is not in the specified server with ID {GUILD_ID}. Disconnecting...")
        await bot.close()  # Отключаем бота, если он не в нужном сервере

# Обработчик сообщений
@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return

        if bot.user in message.mentions and message.reference is None:
            response_gif = random.choice(gif_urls)  # Выбираем один случайный GIF
            await message.reply(response_gif)
            return

        # Проверка сообщений в канале считалки
        if message.channel.id == COUNTING_CHANNEL_ID:
            numbers_in_message = find_numbers(message.content)
            if not numbers_in_message:
                await message.delete()
                warning = await message.channel.send(
                    f"{message.author.mention}, твоё сообщение должно содержать число больше прошлого на 1, не нарушай цепочку!"
                )
                await warning.delete(delay=3)
                return

        # Проверка сообщений в канале для скриншотов
        if message.channel.id == SCREENSHOT_CHANNEL_ID:
            if not message.attachments:
                await message.delete()
                warning = await message.channel.send(
                    f"{message.author.mention}, ты должен отправить скриншот предыдущего сообщения, не нарушай цепочку!"
                )
                await warning.delete(delay=3)
                return

        # Обработка команд
        await bot.process_commands(message)

    except Exception as e:
        print(f"Ошибка в обработке сообщений: {e}")

# Запуск Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# Запуск бота
bot.run(TOKEN)




