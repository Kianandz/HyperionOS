import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "app/static/uploads/backgrounds"


def save_background(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/static/uploads/backgrounds/{file.filename}"


def list_backgrounds() -> list:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return [
        f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))
    ]
