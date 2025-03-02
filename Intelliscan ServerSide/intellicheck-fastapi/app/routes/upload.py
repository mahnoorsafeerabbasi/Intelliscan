# app/routes/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.utils.file_handler import handle_files, run_detection
import os

router = APIRouter()

UPLOAD_DIRECTORY = "uploaded_files"

@router.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    try:
        # Handle file uploads
        file_paths = handle_files(files, UPLOAD_DIRECTORY)
        
        # Run plagiarism detection
        report_path = run_detection(file_paths)
        
        # Return the report file for both display and download
        return FileResponse(
            path=report_path,
            media_type="text/html",
            headers={"Content-Disposition": "inline; filename=report.html"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-report/")
async def download_report():
    report_path = os.path.join(os.getenv("USERPROFILE"), "Downloads", "report.html")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found.")
    
    return FileResponse(
        path=report_path,
        media_type="text/html",
        headers={"Content-Disposition": "attachment; filename=report.html"}
    )
