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
GUILD_ID = 1185300118518378506  # ID сервера
COUNTING_CHANNEL_ID = 1344299177386967120  # Канал считалки
SCREENSHOT_CHANNEL_ID = 1344384380953106512  # Канал скриншотов

# Список URL для GIF
gif_urls = [
    "https://cdn.discordapp.com/attachments/1346943612373569557/1347573414142939279/attachment.gif",
    "https://cdn.discordapp.com/attachments/1322781202851041358/1347037669388980274/attachment.gif",
    "https://cdn.discordapp.com/attachments/1309799105756790794/1309909672446398534/speechmemified_Half_Life_Deathmatch_Source.jpg.gif",
    "https://tenor.com/view/speech-bubble-gif-26412022",
    "https://media.discordapp.net/attachments/1055080776808546353/1177601225542352927/attachment.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367007401115658/attachment.gif?ex=67d12e62&is=67cfdce2&hm=d861e9b134d390a39f71e529b60826e826b3bb9f883c89e6cb200865904cf2cf&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348366855894470697/attachment.gif?ex=67d12e3d&is=67cfdcbd&hm=0de0bb1905b43201f1a9d79a698a2c89bfb0bf4d09da89cad9095a0bba63e612&",
    "https://cdn.jacher.io/f3ac073b88487e1b.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367459392159744/attachment.gif?ex=67d12ecd&is=67cfdd4d&hm=225d51cec802d84090335c6ccbc92ceccfeac3cedd8b946198054399f40c4e45&",
]

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# Создаем объект для бота с необходимыми интентами
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Для доступа к содержимому сообщений

bot = commands.Bot(command_prefix='!', intents=intents)

# Функция для поиска чисел в тексте
def find_numbers(text):
    return re.findall(r'\b\d+\b', text)  # Ищет числа в тексте

# Обработчик сообщений
@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return

        # Проверка, если упомянут бот
        if bot.user in message.mentions and message.reference is None:
            response_gif = random.choice(gif_urls)  # Выбираем случайную гифку
            await message.reply(response_gif)
            return

        # Проверка сообщений в канале считалки
        if message.channel.id == COUNTING_CHANNEL_ID:
            numbers_in_message = find_numbers(message.content)
            if not numbers_in_message:
                await message.delete()
                warning = await message.channel.send(
                    f"{message.author.mention}, сообщение должно содержать хотя бы одно число!"
                )
                await warning.delete(delay=3)
                return

        # Проверка сообщений в канале для скриншотов
        if message.channel.id == SCREENSHOT_CHANNEL_ID:
            if not message.attachments or message.content.strip():  # Сообщение должно быть пустым (только вложение)
                await message.delete()
                warning = await message.channel.send(
                    f"{message.author.mention}, ты должен отправить **только** вложение без текста!"
                )
                await warning.delete(delay=3)
                return

        await bot.process_commands(message)

    except Exception as e:
        print(f"Ошибка в on_message: {e}")

# Запуск Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# Запуск бота
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        print(f'Successfully connected to {guild.name} ({guild.id})')
    else:
        print(f"Bot is not in the specified server with ID {GUILD_ID}. Disconnecting...")
        await bot.close()  # Отключаем бота, если он не в нужном сервере

bot.run(TOKEN)






