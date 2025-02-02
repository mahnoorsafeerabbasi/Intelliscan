from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # Import for serving static files
from app.routes import upload, report
import os
import logging
from decouple import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware (Update the origin for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables for directories
UPLOAD_DIR = config("UPLOAD_DIR", default="uploaded_files")
REPORT_DIR = config("REPORT_DIR", default="reports")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Serve static files
app.mount("/uploaded_files", StaticFiles(directory=UPLOAD_DIR), name="uploaded_files")
app.mount("/reports", StaticFiles(directory=REPORT_DIR), name="reports")

# Include routes
app.include_router(upload.router)
app.include_router(report.router)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting...")
    logger.info(f"Upload directory: {UPLOAD_DIR}")
    logger.info(f"Report directory: {REPORT_DIR}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down...")

# Root endpoint with an HTML response
@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
        <head>
            <title>File Upload and Plagiarism Detection API</title>
        </head>
        <body>
            <h1>Welcome to the File Upload and Plagiarism Detection API</h1>
            <p>Use the form below to upload files and detect plagiarism.</p>
            <form action="/upload/" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple>
                <button type="submit">Upload Files</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
