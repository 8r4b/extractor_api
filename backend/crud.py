from datetime import datetime

from sqlalchemy.orm import Session
from models import User, Resume
from schemas import UserCreate
from utils.hashing import get_password_hash, verify_password



# ---------- User CRUD ----------

def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return user

def create_user(db: Session, email: str, hashed_password: str):
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ---------- Resume CRUD ----------

def create_resume(db: Session, filename: str, skills: str, user_id: int):
    resume = Resume(filename=filename, skills=skills, user_id=user_id)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

def get_resumes_by_user(db: Session, user_id: int):
    return db.query(Resume).filter(Resume.user_id == user_id).all()


def update_user_verification_token(db: Session, email: str, token: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.verification_token = token
        db.commit()
        db.refresh(user)

def update_user_password_reset_token(db: Session, email: str, token: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.password_reset_token = token
        db.commit()
        db.refresh(user)

def get_user_by_password_reset_token(db: Session, token: str):
    return db.query(User).filter(User.password_reset_token == token).first()

def get_user_by_token(db: Session, token: str):
    return db.query(User).filter(User.verification_token == token).first()

def increment_api_calls(db: Session, user: User):
    user.api_calls_this_month += 1
    db.commit()
    db.refresh(user)

def check_api_limit(user: User, limit: int = 1000) -> bool:
    return user.api_calls_this_month < limit

def reset_api_calls(db: Session, user: User):
    user.api_calls_this_month = 0
    user.last_api_reset = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(user)