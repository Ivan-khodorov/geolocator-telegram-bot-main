from aiogram import Bot
from aiogram.types import BotCommand

async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="done", description="Выполнить точку маршрута"),
        BotCommand(command="route", description="Посмотреть маршрут"),
        BotCommand(command="report", description="Статистика за день")
    ])
