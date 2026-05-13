from pydantic import BaseModel

class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str


class LoginSchema(BaseModel):
    email: str
    password: str


class EmergencySchema(BaseModel):
    emergency_type: str
    latitude: float
    longitude: float