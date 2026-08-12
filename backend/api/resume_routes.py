import os
import tempfile
from typing import Optional

from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse

from services.resume_service import generation_pipeline


router = APIRouter(
    prefix="/api",
    tags=["Resume"]
)

# Generate resume endpoint : Generate a tailored resume from an uploaded base resume and job description.
@router.post("/generate")
async def generate_resume(
    file: UploadFile,
    jd: str = Form(...),
    target_role: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
):
   

   
    # Save uploaded resume temporarily
    temp_dir = tempfile.gettempdir()

    file_path = os.path.join(
        temp_dir,
        file.filename
    )

    with open(file_path, "wb") as output_file:
        output_file.write(
            await file.read()
        )

    
    # Start generation pipeline
    return StreamingResponse(
        generation_pipeline(
            file_path=file_path,
            jd=jd,
            target_role=target_role,
            github_url=github_url,
            linkedin_url=linkedin_url,
        ),
        media_type="text/event-stream",
    )

#  Download a generated resume PDF
@router.get("/download/{filename}")
async def download_resume(filename: str):

    file_path = os.path.join(
        tempfile.gettempdir(),
        filename
    )

    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            filename=filename,
            media_type="application/pdf",
        )

    return {
        "error": "File not found"
    }