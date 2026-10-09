import os
from fastapi import UploadFile
from PIL import Image
import time

UPLOAD_DIR = "app/static/uploads/backgrounds"
LOGO_DIR = "app/static/uploads/logo"


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


def save_logo(file: UploadFile) -> str:
    os.makedirs(LOGO_DIR, exist_ok=True)

    image = Image.open(file.file)

    # Biar transparan di PNG nggak rusak
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGBA")
    else:
        image = image.convert("RGB")

    # Resize optimal buat logo (contoh 256x256)
    image.thumbnail((256, 256), Image.Resampling.LANCZOS)

    # Pake timestamp biar nggak kena cache browser pas ganti logo
    new_filename = f"custom_logo_{int(time.time())}.webp"
    file_path = f"{LOGO_DIR}/{new_filename}"

    image.save(file_path, "webp", quality=90, optimize=True)

    return f"/static/uploads/logos/{new_filename}"
