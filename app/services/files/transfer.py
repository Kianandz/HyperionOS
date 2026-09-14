import os
import shutil
from .path import get_safe_path


def transfer_item(src_path: str, dest_dir: str, action: str):
    try:
        full_src = get_safe_path(src_path)
        full_dest = get_safe_path(os.path.join(dest_dir, os.path.basename(full_src)))
        if action == "copy":
            if os.path.isdir(full_src):
                shutil.copytree(full_src, full_dest)
            else:
                shutil.copy2(full_src, full_dest)
        elif action == "move":
            shutil.move(full_src, full_dest)
        return {"status": "success", "message": f"Item successfully {action}ed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def transfer_batch(src_paths: list, dest_dir: str, action: str):
    errors = []
    for p in src_paths:
        res = transfer_item(p, dest_dir, action)
        if res["status"] == "error":
            errors.append(f"{p}: {res['message']}")
    if errors:
        return {"status": "error", "message": ", ".join(errors)}
    return {
        "status": "success",
        "message": f"{len(src_paths)} items successfully {action}ed",
    }
