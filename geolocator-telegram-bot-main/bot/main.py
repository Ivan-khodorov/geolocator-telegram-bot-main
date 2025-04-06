import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot import Config, logger
from bot.set_bot_commands import set_default_commands
from bot.state import States
from bot.keyboard import geolocation_request_button, build_markup_requests_button
from bot.utils.geo_service import GeoService
from bot.utils.auto_report import send_daily_report

from bot.handlers import start
from bot.handlers import done
from bot.handlers import route_report
from bot.handlers import register_admin
from bot.handlers import city_picker



log = logger.get_logger()

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start.router)
dp.include_router(done.router)
dp.include_router(route_report.router)
dp.include_router(register_admin.router)
dp.include_router(city_picker.router)
geo = GeoService()

async def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour=21, minute=0)  # запускается каждый день в 21:00
    scheduler.add_job(send_daily_report, trigger, args=[bot])
    scheduler.start()

@dp.startup()
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await set_default_commands(bot)
    await setup_scheduler(bot)

if __name__ == "__main__":
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)  # Удаляем webhook перед запуском polling
        await dp.start_polling(bot)

    asyncio.run(main())


@dp.message(F.text == "/start")
async def send_hi_buttons(message: Message):
    await message.answer(Config.messages['hello'])

@dp.message(F.text == "/help")
async def send_reference(message: Message):
    await message.answer(Config.messages['help'])

@dp.message(F.text.in_(["/cancel", "отмена"]), state="*")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(Config.messages['cancel'], reply_markup=ReplyKeyboardRemove())

@dp.message(F.text == "/my_place_on_map")
async def get_my_place_on_map(message: Message, state: FSMContext):
    await message.answer(Config.messages['send_location'], reply_markup=geolocation_request_button())
    await state.set_state(States.NAME_LOCATION)

@dp.message(F.content_type == ContentType.LOCATION, state=States.NAME_LOCATION)
async def get_location_name(message: Message, state: FSMContext):
    try:
        if message.location is not None:
            address_str = geo.get_address_from_coords(message.location.latitude, message.location.longitude)
            if address_str:
                await message.answer("Ваше местоположение: " + address_str, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(Config.messages['no_address'])
        else:
            await message.answer(Config.messages['none_location'], reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(Config.args['error'])
    await state.clear()

@dp.message(F.text == "/search")
async def start_search_objects(message: Message, state: FSMContext):
    await message.answer(Config.messages['object_name'])
    await state.set_state(States.OBJECT_LOCATION_1)

@dp.message(F.content_type == ContentType.TEXT, state=States.OBJECT_LOCATION_1)
async def get_object_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.title())
    await message.answer(Config.messages['send_location'], reply_markup=geolocation_request_button())
    await state.set_state(States.OBJECT_LOCATION_2)

@dp.message(F.content_type == ContentType.LOCATION, state=States.OBJECT_LOCATION_2)
async def get_object_location(message: Message, state: FSMContext):
    if message.location:
        await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
        await message.answer(Config.messages['distance'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(States.OBJECT_LOCATION_3)
    else:
        await message.answer(Config.messages['none_location'], reply_markup=ReplyKeyboardRemove())

@dp.message(F.content_type == ContentType.TEXT, state=States.OBJECT_LOCATION_3)
async def get_near_objects(message: Message, state: FSMContext):
    data = await state.get_data()
    radius = message.text.strip()
    try:
        objects = geo.get_nearby_buildings(data['lat'], data['lon'], radius=int(radius))
        if objects:
            await state.update_data(objects=objects)
            await message.answer(Config.messages['places'], reply_markup=build_markup_requests_button(objects))
            await state.set_state(States.OBJECT_LOCATION_4)
        else:
            await message.answer(f"По запросу {data['name']} с радиусом {radius} м ничего не найдено")
            await state.clear()
    except Exception as e:
        await message.answer(Config.args['error'])
        await state.clear()

@dp.callback_query(F.data.startswith("near_object_next_state_"), state=States.OBJECT_LOCATION_4)
async def process_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    objects = data.get("objects", [])
    try:
        index = int(call.data.rsplit("_", 1)[-1])
        if 0 <= index < len(objects):
            obj = objects[index]
            await call.message.answer(f"{obj['address']}")
            await call.message.answer_location(latitude=obj['lat'], longitude=obj['lon'], live_period=1200, proximity_alert_radius=20)
        else:
            await call.message.answer(Config.args['error'])
    except Exception:
        await call.message.answer(Config.args['error'])
    await state.clear()

async def on_startup(bot: Bot) -> None:
    await set_default_commands(bot)


async def main():
    await on_startup(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    asyncio.run(main())