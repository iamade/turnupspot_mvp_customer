from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import asyncio

from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token, get_password_hash
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin, RegistrationResponse
from app.core.exceptions import UnauthorizedException
from app.api.deps import get_current_user
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import secrets

router = APIRouter()

@router.post("/register", response_model=RegistrationResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    activation_token = secrets.token_urlsafe(32)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        date_of_birth=user_data.date_of_birth,
        bio=user_data.bio,
        role=user_data.role,
        is_active=False,
        is_verified=False,
        activation_token=activation_token
    )

    try:
        # Send activation email
        conf = ConnectionConfig(
            MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
            MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
            MAIL_FROM=os.environ.get("MAIL_FROM"),
            MAIL_PORT=int(os.environ.get("MAIL_PORT", 587)),
            MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp-mail.outlook.com"),
            MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", "True") == "True",
            MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", "False") == "True",
            USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", "True") == "True"
        )
        activation_link = f"https://localhost:5173/activate?token={activation_token}"
        message = MessageSchema(
            subject="Activate your TurnUpSpot account",
            recipients=[db_user.email],
            body=f"""
                <h3>Welcome to TurnUpSpot!</h3>
                <p>Click the link below to activate your account:</p>
                <a href='{activation_link}'>{activation_link}</a>
            """,
            subtype="html"
        )
        fm = FastMail(conf)
        asyncio.run(fm.send_message(message))
    except Exception as e:
        print("Email send error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to send activation email: {e}")

    #Only commit if email sent successfully
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "user": db_user,
        "message": "Registration successful! Please check your email to activate your account."
    }


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Please activate your account via the email sent to you.")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/form", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login using OAuth2 form (for compatibility with FastAPI docs)"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/activate")
def activate_user(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.activation_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.is_active = True
    user.is_verified = True
    user.activation_token = None
    db.commit()
    return {"message": "Account activated!"}