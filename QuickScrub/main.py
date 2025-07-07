import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import endpoints

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="QuickScrub API",
    description="A modular API for scrubbing PII from text.",
    version="1.0.0"
)

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a standardized 500 error."""
    logging.error(f"Unhandled exception for {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# Include the API router
app.include_router(endpoints.router, prefix="/api")

# Mount the frontend static files
# This must come after the API routes
try:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
except RuntimeError:
    logging.warning("Frontend 'dist' directory not found. Run 'npm run build' in the 'frontend' directory.")
