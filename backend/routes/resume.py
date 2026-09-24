import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from backend.services.resume_parser import extract_resume_info

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    # Write to /tmp — the working directory may be read-only on Render
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    try:
        loader = PyPDFLoader(temp_path)
        pages = loader.load()
        full_text = "\n".join([page.page_content for page in pages])
        data = extract_resume_info(full_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")
    finally:
        # Always clean up the temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "message": "Resume processed successfully",
        "text_length": len(full_text),
        "preview": full_text[:300],
        "text": full_text,
        "resume_info": data,
    }
