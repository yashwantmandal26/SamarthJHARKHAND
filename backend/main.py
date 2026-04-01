from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config import settings
from backend.data.loader import scheme_db # Ensure data is loaded on startup

app = FastAPI(
    title="Samarth AI - Government Scheme Assistant API",
    description="Multi-agent orchestrated API for identifying Jharkhand government schemes deterministically.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy", "loaded_schemes": len(scheme_db.get_all_schemes())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
