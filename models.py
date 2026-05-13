from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")


class EmergencyRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    emergency_type = Column(String)
    status = Column(String, default="Pending")
    latitude = Column(Float)
    longitude = Column(Float)
    responder_lat = Column(Float, default=0)
    responder_lng = Column(Float, default=0)