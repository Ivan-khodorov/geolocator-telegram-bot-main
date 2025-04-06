from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from database.models import User
from database.session import async_session
from bot.utils.route_creator import create_route_with_points

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    telegram_id = str(message.from_user.id)
    name = message.from_user.full_name

    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            user = User(telegram_id=telegram_id, name=name)
            session.add(user)
            await session.commit()

        fake_points = [
            {"address": "ул. Победы 12", "lat": 51.1, "lon": 71.4, "flyers": 50},
            {"address": "ул. Сейфуллина 20", "lat": 51.12, "lon": 71.41, "flyers": 40}
        ]

        await create_route_with_points(user.id, fake_points, session)

        await message.answer("🗺 Вам назначен маршрут. Готовы к работе!")
