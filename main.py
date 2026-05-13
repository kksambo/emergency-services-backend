
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, engine, Base
from models import User, EmergencyRequest
from schemas import RegisterSchema, LoginSchema, EmergencySchema
from auth import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# LOCATION UPDATE SCHEMA
# =========================
class LocationUpdate(BaseModel):
    responder_lat: float
    responder_lng: float


# =========================
# REGISTER
# =========================
@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "Registered"}


# =========================
# LOGIN
# =========================
@app.post("/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if not existing:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, existing.password):
        raise HTTPException(status_code=400, detail="Wrong password")

    return {
        "id": existing.id,
        "role": existing.role,
        "name": existing.name
    }


# =========================
# CREATE EMERGENCY REQUEST
# =========================
@app.post("/request-emergency/{user_id}")
def request_emergency(
    user_id: int,
    data: EmergencySchema,
    db: Session = Depends(get_db)
):
    req = EmergencyRequest(
        user_id=user_id,
        emergency_type=data.emergency_type,
        latitude=data.latitude,
        longitude=data.longitude
    )

    db.add(req)
    db.commit()

    return {"message": "Emergency requested"}


# =========================
# GET ALL REQUESTS
# =========================
@app.get("/requests")
def get_requests(db: Session = Depends(get_db)):
    return db.query(EmergencyRequest).all()


# =========================
# DISPATCH SERVICE
# =========================
@app.put("/dispatch/{request_id}")
def dispatch(request_id: int, db: Session = Depends(get_db)):
    req = db.query(EmergencyRequest).filter(
        EmergencyRequest.id == request_id
    ).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = "Dispatched"

    # Initial responder location
    req.responder_lat = req.latitude + 0.001
    req.responder_lng = req.longitude + 0.001

    db.commit()

    return {"message": "Responder dispatched"}


# =========================
# UPDATE RESPONDER LOCATION
# =========================
@app.put("/update-location/{request_id}")
def update_location(
    request_id: int,
    data: LocationUpdate,
    db: Session = Depends(get_db)
):
    req = db.query(EmergencyRequest).filter(
        EmergencyRequest.id == request_id
    ).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.responder_lat = data.responder_lat
    req.responder_lng = data.responder_lng

    db.commit()

    return {
        "message": "Responder location updated"
    }


# =========================
# TRACK REQUEST
# =========================
@app.get("/track/{request_id}")
def track(request_id: int, db: Session = Depends(get_db)):
    req = db.query(EmergencyRequest).filter(
        EmergencyRequest.id == request_id
    ).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    return {
        "request_id": req.id,
        "status": req.status,
        "emergency_type": req.emergency_type,

        "user_location": {
            "lat": req.latitude,
            "lng": req.longitude
        },

        "responder_location": {
            "lat": req.responder_lat,
            "lng": req.responder_lng
        }
    }

