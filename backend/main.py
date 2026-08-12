from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.resume_routes import router as resume_router



# FastAPI Application

app = FastAPI(
    title="AI Resume Tailor API",
    description="AI-powered resume tailoring backend",
    version="1.0.0",
)



# CORS Configuration

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes

app.include_router(resume_router)


# Health Check
@app.get("/")
def read_root():
    return {
        "status": "AI Resume Backend is running OK!"
    }


# Run Application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
