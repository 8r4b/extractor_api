
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from utils.skill_extractor import extract_skills_and_feedback_from_text
from utils.file_reader import read_resume
from auth import get_current_user
from database import get_db
from sqlalchemy.orm import Session
from crud import create_resume, check_api_limit, increment_api_calls, check_and_reset_api_usage
from schemas import ResumeFeedback, ErrorResponse

router = APIRouter()

@router.post("/upload-resume/", response_model=ResumeFeedback, responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 402: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}, tags=["Resume"])
async def upload_resume(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if the user's email is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email to use this service.")

    # Check Paddle subscription status
    if user.subscription_status != "active":
        raise HTTPException(status_code=402, detail="Subscription inactive. Please renew your monthly plan.")

    # NEW: Check if the user's billing cycle has reset
    check_and_reset_api_usage(db, user)

    # Enforce API call limit
    if not check_api_limit(user, limit=1000):
        raise HTTPException(status_code=429, detail="API call limit reached for this billing period.")

    # Increment API usage
    increment_api_calls(db, user)

    # Read the uploaded file
    text = await read_resume(file)
    if not text:
        raise HTTPException(status_code=400, detail="Unsupported file or empty content")

    # Extract skills and feedback
    skills, feedback = extract_skills_and_feedback_from_text(text)

    # Ensure skills are properly formatted
    formatted_skills = ", ".join(skills)

    # Store resume data in the database
    resume = create_resume(db, filename=file.filename, skills=formatted_skills, user_id=user.id)
    resume.feedback = feedback
    db.commit()

    return ResumeFeedback(filename=file.filename, skills=skills, feedback=feedback)
