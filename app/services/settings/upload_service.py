import os
from fastapi import UploadFile
from PIL import Image

UPLOAD_DIR = "app/static/uploads/backgrounds"


def save_background(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    image = Image.open(file.file)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

    base_name = file.filename.rsplit(".", 1)[0]
    new_filename = f"{base_name}.webp"
    file_path = f"{UPLOAD_DIR}/{new_filename}"

    image.save(file_path, "webp", quality=80, optimize=True)

    return f"/static/uploads/backgrounds/{new_filename}"


def list_backgrounds() -> list:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return [
        f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))
    ]
