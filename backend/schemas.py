# ---------- Password Reset Schemas ----------

from pydantic import EmailStr

from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator('email')
    def must_be_accepted_email_provider(cls, v):
        allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
        domain = v.split('@')[-1]
        if domain not in allowed_domains:
            raise ValueError('Only Gmail, Yahoo, or Outlook emails are allowed')
        return v
    
    @validator("password")
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

# ---------- Token Schemas ----------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ---------- Resume Schemas ----------

class ResumeResponse(BaseModel):
    id: int
    filename: str
    skills: str
    user_id: int

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetComplete(BaseModel):
    token: str
    new_password: str


# ---------- Standard Response Schemas ----------

class SuccessResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class DataResponse(BaseModel):
    data: dict

class ResumeFeedback(BaseModel):
    filename: str
    skills: list[str]
    feedback: str

    class Config:
        orm_mode = True
