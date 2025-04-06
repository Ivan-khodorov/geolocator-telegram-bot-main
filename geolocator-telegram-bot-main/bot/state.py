from aiogram.fsm.state import State, StatesGroup

class States(StatesGroup):
    NAME_LOCATION = State()
    OBJECT_LOCATION_1 = State()
    OBJECT_LOCATION_2 = State()
    OBJECT_LOCATION_3 = State()
    OBJECT_LOCATION_4 = State()
    ROUTE_WAIT_GPS = State()
    ROUTE_WAIT_PHOTO = State()
    ROUTE_WAIT_CONFIRM = State()
    REGISTER_ADMIN = State()
    ADMIN_CITY_SELECT = State()