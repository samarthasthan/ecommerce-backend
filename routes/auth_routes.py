from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Form, Header,status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal, get_db
import models

from routes.otp_sender import send_otp_email
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
import pyotp
from passlib.context import CryptContext


router = APIRouter()


def generate_otp_secret():
    return pyotp.random_base32()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a CryptContext instance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)



@router.post("/register")
async def register_user(
    first_name: str= Form(...) ,
    middle_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    phone: int= Form(...) ,
    password: str = Form(...),
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
    email: str= Form(...) ,
    otp: str = Form(...),
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


#login


JWT_SECRET = "9d207bf0-10f5-4d8f-a479-22ff5aeff8d1"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer allows you to retrieve the token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a CryptContext instance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)

# Function to verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to get user data based on email
def get_user(db, email: str):
    return db.query(User).filter(User.email == email).first()

# Function to generate JWT token
def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

@router.post("/login")
async def login(
    email: str= Form(...),
    password: str= Form(...),
    db: Session = Depends(get_db)
):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.otp_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not verified",
        )
    
    # Generate a JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token({"email": email}, access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

# Token data model
class Token(BaseModel):
    access_token: str
    token_type: str


def verify_token(authorization: str = Header(...)):
    try:
        token_type, token = authorization.split()
        if token_type != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@router.get("/protected-resource")
async def protected_resource(email: str = Depends(verify_token)):
    # Here, you can use the 'email' parameter for verification or authorization
    return {"message": "Access granted for user with email: " + email}


# Function to generate new access token from refresh token
def refresh_access_token(email: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token({"email": email}, access_token_expires)

@router.post("/refresh-token")
async def refresh_token(refresh_token: str = Form(...)):
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )
        
        # Here, you should also validate the refresh token against stored tokens
        # and perform additional security checks
        
        new_access_token = refresh_access_token(email)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )