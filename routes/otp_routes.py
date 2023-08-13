from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal, get_db

from routes.otp_sender import send_otp_email
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
import pyotp
from passlib.context import CryptContext


router = APIRouter()


def generate_otp_secret():
    return pyotp.random_base32()


# Create a CryptContext instance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)

@router.post("/register")
async def register_user(
    first_name: str ,
    middle_name: str ,
    last_name: str ,
    email: EmailStr ,
    phone: int ,
    password: str ,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        if not existing_user.otp_verified:
            # User exists but OTP is not verified, resend OTP
            send_otp_email(email, existing_user.otp_secret)
            return {"message": "OTP resent for verification."}
        else:
            # User exists and OTP is already verified
            raise HTTPException(status_code=400, detail="Email already registered.")

    try:
        otp_secret = generate_otp_secret()
        hashed_password = get_password_hash(password)
        user = User(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            otp_secret=otp_secret
        )
        db.add(user)
        db.commit()
        send_otp_email(email, otp_secret)
        return {"message": "User registered successfully. OTP sent for verification."}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered.")
     

@router.post("/verify-otp")
async def verify_otp(
    email: str ,
    otp: str ,
    db: SessionLocal = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.otp_verified:
        raise HTTPException(status_code=400, detail="OTP already verified.")
    totp = pyotp.TOTP(user.otp_secret)
    print(otp)
    print(totp.verify(otp,valid_window=20))
    if totp.verify(otp,valid_window=20):
        user.otp_verified = True
        user.is_active = True
        db.commit()
        return {"message": "OTP verified successfully. Account activated."}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
