from fastapi import UploadFile, File, Depends
from app.core.security import verify_session
import os
import shutil
from . import router


@router.post("/upload-bg")
async def upload_background(
    file: UploadFile = File(...), _: str = Depends(verify_session)
):
    upload_dir = "app/static/uploads/backgrounds"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "success",
        "file_url": f"/static/uploads/backgrounds/{file.filename}",
    }
