from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
import crud
from pydantic import BaseModel
from passlib.context import CryptContext
from auth import verify_password, create_access_token
from schemas import UserCreate, UserResponse, PasswordResetRequest, PasswordResetComplete

from uuid import uuid4
from utils.email_utils import send_verification_email
from utils.email_utils import send_password_reset_email
from crud import update_user_verification_token
from crud import update_user_password_reset_token, get_user_by_password_reset_token
import re


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user.password)
    new_user = crud.create_user(db, user.email, hashed_pw)

    token = str(uuid4())
    update_user_verification_token(db, user.email, token)
    send_verification_email(user.email, token)

    return {"message": "Signup successful. Check your email to verify your account."}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully!"}

from schemas import PasswordResetRequest, PasswordResetComplete

@router.post("/forgot-password")
def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = str(uuid4())
    update_user_password_reset_token(db, data.email, token)
    send_password_reset_email(data.email, token)
    return {"message": "Password reset link sent to your email."}

@router.post("/reset-password")
def reset_password(data: PasswordResetComplete, db: Session = Depends(get_db)):
    user = get_user_by_password_reset_token(db, data.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Validate new password
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', data.new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', data.new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', data.new_password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit")

    user.hashed_password = get_password_hash(data.new_password)
    user.password_reset_token = None
    db.commit()
    return {"message": "Password reset successful."}

from pydantic import BaseModel

class ResendVerificationRequest(BaseModel):
    user_email: str

@router.post("/resend-verification-email")
def resend_verification_email(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    # Generate a new verification token
    token = str(uuid4())
    crud.update_user_verification_token(db, data.user_email, token)

    # Send the verification email
    send_verification_email(data.user_email, token)

    return {"message": "Verification email resent successfully. Please check your inbox."}
