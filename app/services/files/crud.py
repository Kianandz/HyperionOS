import os
import shutil
from .path import get_safe_path


def delete_path(target_path: str):
    try:
        full_path = get_safe_path(target_path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return {"status": "success", "message": "Item deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_batch(paths: list):
    errors = []
    for p in paths:
        res = delete_path(p)
        if res["status"] == "error":
            errors.append(f"{p}: {res['message']}")
    if errors:
        return {"status": "error", "message": ", ".join(errors)}
    return {"status": "success", "message": f"{len(paths)} items deleted successfully"}


def create_folder(target_path: str, folder_name: str):
    try:
        full_path = get_safe_path(os.path.join(target_path, folder_name))
        os.makedirs(full_path, exist_ok=True)
        return {"status": "success", "message": "Folder created successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_file(target_path: str, file_name: str):
    try:
        full_path = get_safe_path(os.path.join(target_path, file_name))
        with open(full_path, "w", encoding="utf-8") as f:
            pass
        return {"status": "success", "message": "File created successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def rename_item(target_path: str, new_name: str):
    try:
        full_path = get_safe_path(target_path)
        new_path = os.path.join(os.path.dirname(full_path), new_name)
        os.rename(full_path, new_path)
        return {"status": "success", "message": "Item renamed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
