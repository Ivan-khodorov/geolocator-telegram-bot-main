import os
from aiogram import Bot
from sqlalchemy import select
from database.session import async_session
from database.models import User, Route, Point, PointPhoto
from bot import Config
from datetime import datetime

async def send_daily_report(bot: Bot):
    async with async_session() as session:
        users = await session.scalars(select(User))
        for user in users:
            route = await session.scalar(
                select(Route).where(Route.user_id == user.id).order_by(Route.date.desc()).limit(1)
            )
            if not route:
                continue

            points = await session.scalars(
                select(Point).where(Point.route_id == route.id)
            )

            completed = [p for p in points if p.is_completed]
            total = len(list(points))

            report = f"📤 <b>Отчёт сотрудника {user.name}</b>\n"
            report += f"📅 Дата: {route.date.strftime('%d.%m.%Y')}\n"
            report += f"✅ Выполнено: {len(completed)} из {total}\n\n"

            await bot.send_message(Config.ADMIN_CHAT_ID, report, parse_mode="HTML")

            for p in completed:
                time = p.completed_at.strftime('%H:%M') if p.completed_at else "время неизвестно"
                await bot.send_message(Config.ADMIN_CHAT_ID, f"📍 {p.address} — {time}")

                photos = await session.scalars(select(PointPhoto).where(PointPhoto.point_id == p.id))
                for photo in photos:
                    try:
                        with open(photo.filepath, "rb") as f:
                            await bot.send_photo(Config.ADMIN_CHAT_ID, f)
                    except:
                        await bot.send_message(Config.ADMIN_CHAT_ID, "⚠️ Ошибка при отправке фото.")
