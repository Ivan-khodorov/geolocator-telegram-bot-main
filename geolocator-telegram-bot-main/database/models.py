from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, ForeignKey, Text, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# 👤 Сотрудник (исполнитель)
class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    telegram_id = mapped_column(String(64), unique=True, nullable=False)
    name = mapped_column(String(256), nullable=False)
    role = mapped_column(String(32), nullable=False, default="user")  # user | admin
    city = mapped_column(String(128), nullable=True)


# 📆 Маршрут (привязан к пользователю и дате)
class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="routes")
    points = relationship("Point", back_populates="route")


# 📍 Отдельная точка маршрута (подъезд)
class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    address = Column(String(255), nullable=False)
    lat = Column(Float)
    lon = Column(Float)
    flyer_count = Column(Integer, default=0)

    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))

    route = relationship("Route", back_populates="points")
    photos = relationship("PointPhoto", back_populates="point")


# 🖼 Фотофиксация с точки
class PointPhoto(Base):
    __tablename__ = "point_photos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    point_id = Column(Integer, ForeignKey("points.id"))
    filepath = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="photos")
    point = relationship("Point", back_populates="photos")


# 📊 Ежедневный отчёт (можно агрегировать)
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True), server_default=func.now())
    completed_points = Column(Integer)
    total_points = Column(Integer)
    notes = Column(Text)

    user = relationship("User")

class CityZone(Base):
    __tablename__ = "city_zones"

    id = mapped_column(Integer, primary_key=True)
    city_name = mapped_column(String(128), nullable=False)
    polygon_coords = mapped_column(JSON, nullable=False)  # Список координат полигона
    created_by = mapped_column(ForeignKey("users.id"))
