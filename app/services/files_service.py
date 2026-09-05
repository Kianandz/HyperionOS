import os
import shutil
import stat
import datetime
import zipfile

BASE_PATH = os.path.abspath(os.path.expanduser("~"))
MAX_EDIT_SIZE = 5 * 1024 * 1024  # 5 MB limit

def get_safe_path(target_path: str) -> str:
    target_path = target_path or ""
    clean_relative = target_path.lstrip("/").lstrip("\\")
    full_path = os.path.abspath(os.path.join(BASE_PATH, clean_relative))
    
    if os.path.commonpath([BASE_PATH, full_path]) != BASE_PATH:
        raise PermissionError("Akses di luar root direktori tidak diizinkan.")
    return full_path

def get_directory_contents(target_path: str = ""):
    try:
        full_path = get_safe_path(target_path)
        if not os.path.exists(full_path):
            return {"status": "error", "message": "Path tidak ditemukan"}

        items = []
        for entry in os.scandir(full_path):
            try:
                file_stat = entry.stat(follow_symlinks=False)
                permission_str = stat.filemode(file_stat.st_mode)
                is_dir = entry.is_dir(follow_symlinks=False)
                size_bytes = file_stat.st_size if not is_dir else 0
                mod_time = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            except (PermissionError, FileNotFoundError, OSError):
                permission_str = "----------"
                is_dir = entry.is_dir(follow_symlinks=False) if hasattr(entry, 'is_dir') else False
                size_bytes = 0
                mod_time = "-"

            items.append({
                "name": entry.name,
                "is_dir": is_dir,
                "size_bytes": size_bytes,
                "path": os.path.relpath(entry.path, BASE_PATH).replace("\\", "/"),
                "permissions": permission_str,
                "last_modified": mod_time
            })

        return {
            "status": "success",
            "current_path": target_path.strip("/"),
            "items": sorted(items, key=lambda x: (not x["is_dir"], x["name"].lower()))
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_path(target_path: str):
    try:
        full_path = get_safe_path(target_path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return {"status": "success", "message": "Item berhasil dihapus"}
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
    return {"status": "success", "message": f"{len(paths)} item berhasil dihapus"}

def create_folder(target_path: str, folder_name: str):
    try:
        full_path = get_safe_path(os.path.join(target_path, folder_name))
        os.makedirs(full_path, exist_ok=True)
        return {"status": "success", "message": "Folder berhasil dibuat"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_file(target_path: str, file_name: str):
    try:
        full_path = get_safe_path(os.path.join(target_path, file_name))
        with open(full_path, 'w', encoding='utf-8') as f:
            pass
        return {"status": "success", "message": "File berhasil dibuat"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def rename_item(target_path: str, new_name: str):
    try:
        full_path = get_safe_path(target_path)
        new_path = os.path.join(os.path.dirname(full_path), new_name)
        os.rename(full_path, new_path)
        return {"status": "success", "message": "Nama berhasil diubah"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        return {"status": "success", "message": f"Item berhasil di-{action}"}
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
    return {"status": "success", "message": f"{len(src_paths)} item berhasil di-{action}"}

def read_file(target_path: str):
    try:
        full_path = get_safe_path(target_path)
        if os.path.getsize(full_path) > MAX_EDIT_SIZE:
            return {"status": "error", "message": "File terlalu besar untuk diedit (maksimal 5MB)."}

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except UnicodeDecodeError:
        return {"status": "error", "message": "File biner tidak dapat diedit sebagai teks."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def write_file(target_path: str, content: str):
    try:
        full_path = get_safe_path(target_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": "File berhasil disimpan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def extract_archive(target_path: str, dest_dir: str = None):
    try:
        full_path = get_safe_path(target_path)
        extract_to = get_safe_path(dest_dir) if dest_dir else os.path.dirname(full_path)

        if full_path.endswith('.zip'):
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    member_path = os.path.abspath(os.path.join(extract_to, member))
                    if os.path.commonpath([extract_to, member_path]) != extract_to:
                        raise PermissionError(f"File berbahaya terdeteksi dalam ZIP: {member}")
                zip_ref.extractall(extract_to)
        else:
            shutil.unpack_archive(full_path, extract_dir=extract_to)

        return {"status": "success", "message": "Ekstraksi berhasil"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def compress_items(paths: list, current_path: str, zip_name: str = "archive.zip"):
    try:
        if not zip_name.endswith('.zip'):
            zip_name += '.zip'
            
        target_dir = get_safe_path(current_path)
        zip_full_path = os.path.join(target_dir, zip_name)

        with zipfile.ZipFile(zip_full_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
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

        return {"status": "success", "message": f"Arsip {zip_name} berhasil dibuat"}
    except Exception as e:
        return {"status": "error", "message": str(e)}