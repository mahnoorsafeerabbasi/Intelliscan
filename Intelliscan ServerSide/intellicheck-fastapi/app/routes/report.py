# app/routes/report.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/report/")
async def get_report():
    try:
        # Ensure the report exists
        report_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'report.html')
        if os.path.exists(report_path):
            return HTMLResponse(content=open(report_path, "r").read())
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
