import os
from .config import MAX_EDIT_SIZE
from .path import get_safe_path


def read_file(target_path: str):
    try:
        full_path = get_safe_path(target_path)

        if target_path == "/etc/samba/smb.conf" and not os.path.exists(full_path):
            default_smb = """[global]
    workgroup = WORKGROUP
    server string = Hyperion Samba Server
    server role = standalone server
    log file = /var/log/samba/%m.log
    max log size = 50
    dns proxy = no
    map to guest = bad user

[Public_Share]
    path = /home/kianandz/public
    public = yes
    writable = yes
    guest ok = yes
    force user = kianandz
"""
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(default_smb)

        if os.path.getsize(full_path) > MAX_EDIT_SIZE:
            return {
                "status": "error",
                "message": "File is too large to edit (maximum 5MB).",
            }

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content}

    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": "Binary file cannot be edited as text.",
        }
    except PermissionError:
        return {
            "status": "error",
            "message": "Access denied! /etc/samba folder requires permission (Run chown in terminal first).",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def write_file(target_path: str, content: str):
    try:
        full_path = get_safe_path(target_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": "File saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
