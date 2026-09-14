import os
from .config import BASE_PATH


def get_safe_path(target_path: str) -> str:
    if target_path == "/etc/samba/smb.conf":
        return target_path

    target_path = target_path or ""
    clean_relative = target_path.lstrip("/").lstrip("\\")
    full_path = os.path.abspath(os.path.join(BASE_PATH, clean_relative))

    if os.path.commonpath([BASE_PATH, full_path]) != BASE_PATH:
        raise PermissionError("Access outside the root directory is not allowed.")
    return full_path
