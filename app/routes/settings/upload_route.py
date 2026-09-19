from fastapi import UploadFile, File, Depends
from app.core.security import verify_session
from . import router
from app.services.settings import upload_service

@router.post("/upload-bg")
async def upload_background(
    file: UploadFile = File(...), _: str = Depends(verify_session)
):
    file_url = upload_service.save_background(file)
    return {
        "status": "success",
        "file_url": file_url,
    }