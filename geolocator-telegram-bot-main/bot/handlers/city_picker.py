from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.state import States
from database.session import async_session
from database.models import User

router = Router()

TOP_CITIES = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Челябинск", "Самара", "Ростов-на-Дону", "Уфа"
]

@router.message(F.text == "/cities")
async def cmd_cities(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    async with async_session() as session:
        user = await session.scalar(
            User.__table__.select().where(User.telegram_id == telegram_id)
        )
        if user is None or user.role != "admin":
            await message.answer("⛔ Эта команда доступна только администраторам.")
            return

    # Кнопки с названиями городов
    buttons = [
        [types.InlineKeyboardButton(text=city, callback_data=f"city_{city}")]
        for city in TOP_CITIES
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("🏙 Выберите город:", reply_markup=markup)
    await state.set_state(States.ADMIN_CITY_SELECT)

@router.callback_query(F.data.startswith("city_"))
async def handle_city_choice(callback: CallbackQuery, state: FSMContext):
    city = callback.data.replace("city_", "")
    await state.update_data(city=city)
    await callback.message.edit_text(f"✅ Город выбран: {city}\n\nТеперь можно перейти к выбору области.")
    await callback.answer()
