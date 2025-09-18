from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
import crud

from user_routes import router as user_router
from resume_routes import router as resume_router
from paddle_routes import router as paddle_router
import create_tables
import uvicorn


app = FastAPI()

# 2. Add the middleware and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Monthly Reset Scheduler ---
def monthly_api_reset():
    """Function to be called by the scheduler."""
    db = SessionLocal()
    try:
        crud.reset_all_user_api_calls(db)
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(monthly_api_reset, 'cron', day=1, hour=0) # Runs at midnight on the 1st of every month

@app.on_event("startup")
def startup_event():
    scheduler.start()
# --- End of Scheduler Setup ---


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://skills-five-nu.vercel.app",  # Deployed frontend URL
        "https://skills-h2qytuj01-mohameds-projects-18c8d61d.vercel.app"  # Another deployed frontend URL (if applicable)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables.create_tables()  # Creates tables on startup (optional)

app.include_router(user_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(paddle_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)