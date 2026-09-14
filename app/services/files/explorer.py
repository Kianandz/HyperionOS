import os
import stat
import datetime
from .config import BASE_PATH
from .path import get_safe_path


def get_directory_contents(target_path: str = ""):
    try:
        full_path = get_safe_path(target_path)
        if not os.path.exists(full_path):
            return {"status": "error", "message": "Path not found"}

        items = []
        for entry in os.scandir(full_path):
            try:
                file_stat = entry.stat(follow_symlinks=False)
                permission_str = stat.filemode(file_stat.st_mode)
                is_dir = entry.is_dir(follow_symlinks=False)
                size_bytes = file_stat.st_size if not is_dir else 0
                mod_time = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                )
            except (PermissionError, FileNotFoundError, OSError):
                permission_str = "----------"
                is_dir = (
                    entry.is_dir(follow_symlinks=False)
                    if hasattr(entry, "is_dir")
                    else False
                )
                size_bytes = 0
                mod_time = "-"

            items.append(
                {
                    "name": entry.name,
                    "is_dir": is_dir,
                    "size_bytes": size_bytes,
                    "path": os.path.relpath(entry.path, BASE_PATH).replace("\\", "/"),
                    "permissions": permission_str,
                    "last_modified": mod_time,
                }
            )

        return {
            "status": "success",
            "current_path": target_path.strip("/"),
            "items": sorted(items, key=lambda x: (not x["is_dir"], x["name"].lower())),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
