import discord
import os
import random
import threading
import re
from discord.ext import commands
from flask import Flask

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Идентификаторы серверов и каналов
GUILD_ID = 1185300118518378506  # Целевой сервер
FORUM_CHANNEL_ID = 1294728720225144832  # Канал форума
COUNTING_CHANNEL_ID = 1344299177386967120  # Канал считалки
SCREENSHOT_CHANNEL_ID = 1344388680953106512  # Канал скриншотов

# Настройки бота
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask-сервер
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
    "https://media.discordapp.net/attachments/1055080776808546353/1177601225542352927/attachment.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367007401115658/attachment.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348366855894470697/attachment.gif",
    "https://cdn.jacher.io/f3ac073b88487e1b.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367459392159744/attachment.gif",
]

# Функция поиска чисел в тексте
def find_numbers(text):
    return [int(num) for num in re.findall(r'\b\d+\b', text)]  # Ищет все числа

# Событие подключения бота
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    
    # Если бот не на целевом сервере, он покидает его
    for guild in bot.guilds:
        if guild.id != GUILD_ID:
            await guild.leave()
            print(f"Bot left server: {guild.name} ({guild.id})")
    
    print(f'Connected to {guild.name} ({guild.id})')

# Проверка сообщений в форуме
async def check_forum_post(thread):
    numbers_in_title = find_numbers(thread.name)
    
    # Получение первого сообщения в ветке
    async for message in thread.history(limit=1, oldest_first=True):
        numbers_in_message = find_numbers(message.content)

        # Если нет чисел в названии или сообщении, отправляем предупреждение
        if (not numbers_in_title and not numbers_in_message) or \
           (numbers_in_title and min(numbers_in_title) < 10000) or \
           (numbers_in_message and min(numbers_in_message) < 10000):
            await thread.send("Кажется, ты не указал ID уровня! Напиши его, чтобы люди могли его легко найти!")

# Обработчик для создания ветки в форуме
@bot.event
async def on_thread_create(thread):
    if thread.parent_id == FORUM_CHANNEL_ID:
        await check_forum_post(thread)

# Обработчик сообщений
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Если бот упомянут, отправляем случайный GIF
    if bot.user in message.mentions and message.reference is None:
        response_gif = random.choice(gif_urls)  # Выбираем один случайный GIF
        await message.reply(response_gif)
        return

    # Проверка на канал считалки
    if message.channel.id == COUNTING_CHANNEL_ID:
        if not find_numbers(message.content):  # Если в тексте нет числа
            await message.delete()
            warning = await message.channel.send(f"{message.author.mention}, в сообщении должно быть число!")
            await warning.delete(delay=3)
            return

    # Проверка на канал скриншотов
    if message.channel.id == SCREENSHOT_CHANNEL_ID:
        if not message.attachments:  # Если нет вложений
            await message.delete()
            warning = await message.channel.send(f"{message.author.mention}, сюда можно отправлять только скриншоты!")
            await warning.delete(delay=3)
            return

    # Обработка команд
    await bot.process_commands(message)

# Запуск Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# Запуск бота
bot.run(TOKEN)







