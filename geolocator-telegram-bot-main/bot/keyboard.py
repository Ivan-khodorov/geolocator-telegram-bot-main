from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

geolocation_request_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Отправить локацию", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def build_markup_requests_button(objects: list[dict]) -> InlineKeyboardMarkup:
    keyboard = []
    for idx, obj in enumerate(objects):
        button = InlineKeyboardButton(
            text=obj["address"],
            callback_data=f"near_object_next_state_{idx}"
        )
        keyboard.append([button])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)