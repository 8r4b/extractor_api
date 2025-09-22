from datetime import datetime, timedelta
import logging
logger = logging.getLogger("crud")
logging.basicConfig(level=logging.INFO)
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


def reset_all_user_api_calls(db: Session):
    """Resets the api_calls_this_month counter for all users to 0."""
    try:
        num_rows_updated = db.query(User).update({User.api_calls_this_month: 0})
        db.commit()
        logger.info(f"Successfully reset API call counts for {num_rows_updated} users.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting API call counts: {e}")

def increment_api_calls(db: Session, user: User):
    user.api_calls_this_month += 1
    # Optionally increment free_trial_calls here if you want to track all API usage
    db.commit()
    db.refresh(user)

def check_api_limit(user: User, limit: int = 1000) -> bool:
    return user.api_calls_this_month < limit

def reset_api_calls(db: Session, user: User):
    user.api_calls_this_month = 0
    user.last_api_reset = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(user)

def check_and_reset_api_usage(db: Session, user: User):
    """Checks if a user's billing cycle has reset and updates their API count."""
    if not user.subscription_start_date:
        return # Do nothing if they've never subscribed

    # Check if one month has passed since the last reset
    # A simple approach is to check if it's a new month relative to their start day
    now = datetime.utcnow()
    # A more accurate way is to see if 30 days have passed, or use a dateutil library.
    # For simplicity, let's use a 30-day window.
    if user.last_api_reset and (now - datetime.fromisoformat(user.last_api_reset)) > timedelta(days=30):
        user.api_calls_this_month = 0
        user.last_api_reset = now.isoformat()
        db.commit()
        db.refresh(user)