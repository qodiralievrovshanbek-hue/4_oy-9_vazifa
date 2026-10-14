import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BotCommand


bot = Bot(token="8914205774:AAEyuYQaiyMWIAOON07DO3YfHHtoWe7tc2k")
dispatcher = Dispatcher()

@dispatcher.message(Command("start"))
async def start(message: Message):
    await message.answer("Salom bolajonlar😁")

@dispatcher.message(Command("maslahat"))
async def maslahat(message: Message):
    await message.answer("O'qi ukam☝")

@dispatcher.message(Command("yordam"))
async def yordam(message: Message):
    await message.answer("Yordamnni faqat o'zingdan kut!🗿")

@dispatcher.message(Command("admin"))
async def admin(message: Message):
    await message.answer("Admin ==> @maxmudovcss")

@dispatcher.message(F.voice)
@dispatcher.message(F.contact)
@dispatcher.message(F.location)
@dispatcher.message(F.video)
@dispatcher.message(F.photo)
@dispatcher.message(F.text)
async def get_text(message: Message):
    if message.voice:
        print(message.voice.duration)
    elif message.contact:
        print(message.contact.phone_number)
    elif message.location:
        print(message.location.latitude, message.location.longitude)
    elif message.video:
        print(message.video.file_id)
    elif message.photo:
        print(message.photo, message.photo[-1].file_id)

    chat_id = message.chat.id
    await message.copy_to(chat_id, message.message_thread_id)

async def main():
    await bot.set_my_commands(commands=[
            BotCommand(command="start", description="Boshlash"),
            BotCommand(command="maslahat", description="Maslahatlar"),
            BotCommand(command="yordam", description="Yordamlar"),
            BotCommand(command="admin", description="Admin bilan bog'lanish")
        ])
    await dispatcher.start_polling(bot)

asyncio.run(main())