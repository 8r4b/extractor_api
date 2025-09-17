from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from user_routes import router as user_router
from resume_routes import router as resume_router
import create_tables
import uvicorn

app = FastAPI()

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

@app.get("/")
def read_root():
    return {"message": "Backend API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)