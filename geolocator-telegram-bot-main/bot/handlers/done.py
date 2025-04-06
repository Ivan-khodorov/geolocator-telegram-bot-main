from aiogram.filters import StateFilter
from aiogram import Router, F, types
from aiogram.types import Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from bot.state import States

from sqlalchemy import select
from database.models import Point, PointPhoto
from database.session import async_session
from datetime import datetime
from bot.utils.photo_validator import is_near_point

router = Router()


@router.message(F.text == "/done")
async def done_start(message: Message, state: FSMContext):
	await message.answer("📍 Отправьте геолокацию на текущей точке", reply_markup=types.ReplyKeyboardMarkup(
		keyboard=[[types.KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
		resize_keyboard=True
	))
	await state.set_state(States.ROUTE_WAIT_GPS)


@router.message(StateFilter(States.ROUTE_WAIT_GPS), F.content_type == ContentType.LOCATION)
async def receive_gps(message: Message, state: FSMContext):
	await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
	await message.answer("📸 Теперь отправьте фото разложенных листовок", reply_markup=ReplyKeyboardRemove())
	await state.set_state(States.ROUTE_WAIT_PHOTO)


@router.message(StateFilter(States.ROUTE_WAIT_PHOTO), F.content_type == ContentType.PHOTO)
async def receive_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    lat, lon = data.get("lat"), data.get("lon")
    photo_id = message.photo[-1].file_id

    async with async_session() as session:
        user_id = message.from_user.id

        # Найдём ближайшую точку маршрута
        points = await session.execute(
            select(Point).join(Point.route).where(
                Point.is_completed == False,
                Point.route.has(user_id=user_id)
            )
        )
        point = None
        for p in points.scalars():
            if is_near_point(lat, lon, p.lat, p.lon):
                point = p
                break

        if not point:
            await message.answer("❌ Вы слишком далеко от назначенной точки.")
            await state.clear()
            return

        # ✅ Сохраняем фото
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{user_id}_{point.id}_{timestamp}.jpg"
        path = f"media/photos/{filename}"
        await message.bot.download(file=photo_id, destination=path)

        # Записываем в БД
        photo = PointPhoto(user_id=user_id, point_id=point.id, filepath=path)
        point.is_completed = True
        point.completed_at = datetime.utcnow()

        session.add(photo)
        await session.commit()

        await message.answer("✅ Точка успешно зафиксирована!")
    await state.clear()