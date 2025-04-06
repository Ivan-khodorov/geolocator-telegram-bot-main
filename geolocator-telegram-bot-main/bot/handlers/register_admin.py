from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.state import States
from database.session import async_session
from sqlalchemy import select
from database.models import User

router = Router()

@router.message(F.text == "/register_admin")
async def ask_name(message: Message, state: FSMContext):
    await message.answer("Введите своё имя для регистрации администратора:")
    await state.set_state(States.REGISTER_ADMIN)

@router.message(States.REGISTER_ADMIN)
async def save_admin(message: Message, state: FSMContext):
    async with async_session() as session:
        telegram_id = str(message.from_user.id)

        # Проверка — уже зарегистрирован?
        existing = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if existing:
            await message.answer(f"Вы уже зарегистрированы как: {existing.role}.")
        else:
            admin = User(
                telegram_id=telegram_id,
                name=message.text,
                role="admin"
            )
            session.add(admin)
            await session.commit()
            await message.answer("✅ Вы зарегистрированы как администратор!")

    await state.clear()
