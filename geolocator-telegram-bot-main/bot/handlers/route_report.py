from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from database.session import async_session
from database.models import User, Route, Point, PointPhoto
from bot.utils.auto_report import send_daily_report
from bot import Config
from datetime import datetime

router = Router()

@router.message(F.text == "/route")
async def show_route(message: Message):
    telegram_id = str(message.from_user.id)

    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start.")
            return

        route = await session.scalar(
            select(Route).where(Route.user_id == user.id).order_by(Route.date.desc()).limit(1)
        )
        if not route:
            await message.answer("Маршрут не найден.")
            return

        points = await session.scalars(
            select(Point).where(Point.route_id == route.id)
        )

        if not points:
            await message.answer("Маршрут пуст.")
            return

        text = "🗺 <b>Ваш маршрут:</b>\n\n"
        for p in points:
            status = "✅" if p.is_completed else "🔲"
            text += f"{status} {p.address}\n"

        await message.answer(text, parse_mode="HTML")

@router.message(F.text == "/report")
async def show_report(message: Message):
    telegram_id = str(message.from_user.id)

    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            await message.answer("Вы не зарегистрированы.")
            return

        route = await session.scalar(
            select(Route).where(Route.user_id == user.id).order_by(Route.date.desc()).limit(1)
        )
        if not route:
            await message.answer("Маршрут не найден.")
            return

        points = await session.scalars(
            select(Point).where(Point.route_id == route.id)
        )

        completed = [p for p in points if p.is_completed]
        total = len(list(points))

        text = f"📊 <b>Отчёт за {route.date.strftime('%d.%m.%Y')}</b>\n"
        text += f"Пройдено точек: {len(completed)} из {total}\n\n"

        await message.answer(text, parse_mode="HTML")

        for point in completed:
            address = point.address
            time = point.completed_at.strftime('%H:%M') if point.completed_at else "время неизвестно"

            photos = await session.scalars(
                select(PointPhoto).where(PointPhoto.point_id == point.id)
            )
            photo_paths = [photo.filepath for photo in photos]

            await message.answer(f"✅ <b>{address}</b>\n🕒 {time}", parse_mode="HTML")

            for path in photo_paths:
                try:
                    with open(path, "rb") as f:
                        await message.answer_photo(f)
                except Exception:
                    await message.answer("⚠️ Ошибка при загрузке фото.")
@router.message(F.text == "/admin_report")
async def trigger_admin_report(message: Message):
    if message.from_user.id != Config.ADMIN_CHAT_ID:
        await message.answer("⛔ Только администратор может вызывать этот отчёт.")
        return

    await message.answer("📡 Отправляю отчёты...")
    await send_daily_report(message.bot)
    await message.answer("✅ Отчёты отправлены.")

