from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Route, Point
from sqlalchemy import select
from datetime import datetime


async def create_route_with_points(user_id: int, points: list[dict], session: AsyncSession) -> Route:
    """
    Создание маршрута с точками для пользователя
    :param user_id: ID пользователя
    :param points: список точек [{address, lat, lon, flyers}]
    :param session: активная сессия SQLAlchemy
    :return: созданный маршрут
    """
    # Создаём маршрут
    route = Route(user_id=user_id, date=datetime.utcnow())
    session.add(route)
    await session.flush()  # получаем ID маршрута без коммита

    # Добавляем точки
    for p in points:
        point = Point(
            route_id=route.id,
            address=p["address"],
            lat=p["lat"],
            lon=p["lon"],
            flyer_count=p.get("flyers", 0)
        )
        session.add(point)

    await session.commit()
    return route
