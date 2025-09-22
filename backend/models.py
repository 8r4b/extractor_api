from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True, index=True)  # for email verification
    password_reset_token = Column(String, nullable=True, index=True)  # for password reset
    api_calls_this_month = Column(Integer, default=0)  # Track API calls per month
    last_api_reset = Column(String, nullable=True)  # Store last reset date (ISO string)
    subscription_status = Column(String, default="inactive")  # Paddle subscription status
    subscription_start_date = Column(DateTime, nullable=True) # Add this line
    free_trial_calls = Column(Integer, default=0)  # Track free trial usage

    resumes = relationship("Resume", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    skills = Column(Text, nullable=True)  # Add this
    feedback = Column(Text, nullable=True)  # Added feedback column
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="resumes")
