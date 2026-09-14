import os
import shutil
import zipfile
from .path import get_safe_path


def extract_archive(target_path: str, dest_dir: str = None):
    try:
        full_path = get_safe_path(target_path)
        extract_to = get_safe_path(dest_dir) if dest_dir else os.path.dirname(full_path)

        if full_path.endswith(".zip"):
            with zipfile.ZipFile(full_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    member_path = os.path.abspath(os.path.join(extract_to, member))
                    if os.path.commonpath([extract_to, member_path]) != extract_to:
                        raise PermissionError(
                            f"Dangerous file detected in ZIP: {member}"
                        )
                zip_ref.extractall(extract_to)
        else:
            shutil.unpack_archive(full_path, extract_dir=extract_to)

        return {"status": "success", "message": "Extraction successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def compress_items(paths: list, current_path: str, zip_name: str = "archive.zip"):
    try:
        if not zip_name.endswith(".zip"):
            zip_name += ".zip"

        target_dir = get_safe_path(current_path)
        zip_full_path = os.path.join(target_dir, zip_name)

        with zipfile.ZipFile(zip_full_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for item_rel in paths:
                item_full = get_safe_path(item_rel)
                if os.path.isdir(item_full):
                    for root, _, files in os.walk(item_full):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, target_dir)
                            zip_file.write(file_path, arcname)
                else:
                    arcname = os.path.basename(item_full)
                    zip_file.write(item_full, arcname)

        return {
            "status": "success",
            "message": f"Archive {zip_name} created successfully",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
