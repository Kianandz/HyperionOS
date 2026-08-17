import os
import shutil

BASE_PATH = os.path.expanduser("~")

def get_directory_contents(target_path: str = ""):

    full_path = os.path.abspath(os.path.join(BASE_PATH, target_path.lstrip("/")))
    
    if not os.path.exists(full_path):

        return {"status": "error", "message": "Path tidak ditemukan"}

    items = []

    try:

        for entry in os.scandir(full_path):

            stat = entry.stat()

            items.append({

                "name": entry.name,

                "is_dir": entry.is_dir(),

                "size_bytes": stat.st_size if not entry.is_dir() else 0,

                "path": os.path.relpath(entry.path, BASE_PATH)

            })

        return {

            "status": "success",

            "current_path": target_path,

            "items": sorted(items, key=lambda x: (not x["is_dir"], x["name"].lower()))

        }
    
    except Exception as e:

        return {"status": "error", "message": str(e)}
    

def delete_path(target_path: str):

    full_path = os.path.abspath(os.path.join(BASE_PATH, target_path.lstrip("/")))

    try:

        if os.path.isdir(full_path):

            shutil.rmtree(full_path)
        else:

            os.remove(full_path)

        return {"status": "success", "message": "Item berhasil dihapus"}
    
    except Exception as e:

        return {"status": "error", "message": str(e)}
    