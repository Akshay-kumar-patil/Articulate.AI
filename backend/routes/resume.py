import os
import shutil
from fastapi import APIRouter, UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
from backend.services.resume_parser import extract_resume_info

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile=File(...)):
    # temperory storing in disk
    temp_path=f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    loader=PyPDFLoader(temp_path)
    pages=loader.load()
    full_text="\n".join([page.page_content for page in pages])
    data=extract_resume_info(full_text)

    os.remove(temp_path)

    return{
        "message": "Resume processed successfully",
        "text_length": len(full_text),
        "preview": full_text[:300],
        "text": full_text,
        "resume_info": data
    }

