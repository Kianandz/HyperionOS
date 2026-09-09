import os
import shutil
import stat
import datetime
import zipfile
import subprocess
import glob

BASE_PATH = os.path.abspath(os.path.expanduser("~"))
MAX_EDIT_SIZE = 5 * 1024 * 1024  # 5 MB limit
SHARE_CONF_DIR = "/etc/samba/shares.conf.d"

def get_safe_path(target_path: str) -> str:
    # Whitelist khusus untuk config Samba
    if target_path == "/etc/samba/smb.conf":
        return target_path

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
        
        # Auto-create khusus smb.conf kalau belum ada
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
            # Bikin file otomatis
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(default_smb)

        if os.path.getsize(full_path) > MAX_EDIT_SIZE:
            return {"status": "error", "message": "File terlalu besar untuk diedit (maksimal 5MB)."}

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
        
    except UnicodeDecodeError:
        return {"status": "error", "message": "File biner tidak dapat diedit sebagai teks."}
    except PermissionError:
        return {"status": "error", "message": "Akses ditolak! Folder /etc/samba butuh permission (Jalankan chown dulu di terminal)."}
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

# ===============================
# SAMBA MANAGEMENT FUNCTIONS
# ===============================
def init_samba_global():
    os.makedirs(SHARE_CONF_DIR, exist_ok=True)
    conf_path = "/etc/samba/smb.conf"
    
    if not os.path.exists(conf_path):
        default_smb = f"""[global]
    workgroup = WORKGROUP
    server string = Hyperion Samba Server
    server role = standalone server
    log file = /var/log/samba/%m.log
    max log size = 50
    dns proxy = no
    map to guest = bad user
    # Load semua config individual dari folder shares
    include = {SHARE_CONF_DIR}/*.conf
"""
        with open(conf_path, 'w', encoding='utf-8') as f:
            f.write(default_smb)

def parse_smb_conf():
    init_samba_global()
    shares = []
    import glob, os
    
    for conf_file in glob.glob(f"{SHARE_CONF_DIR}/*.conf"):
        name = os.path.basename(conf_file).replace('.conf', '')
        current = {
            "name": name, "path": "-", "guest_ok": "No", "writable": "No", 
            "browseable": "Yes", "valid_users": "", "create_mask": "0755", 
            "directory_mask": "0755", "raw": ""
        }
        
        with open(conf_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            current["raw"] = raw_content
            
            for line in raw_content.splitlines():
                line = line.strip()
                if "=" in line and not line.startswith(("#", "[", ";")):
                    k, v = [x.strip() for x in line.split("=", 1)]
                    k = k.lower()
                    if k == "path": current["path"] = v
                    elif k in ["guest ok", "public"]: current["guest_ok"] = "Yes" if v.lower() == "yes" else "No"
                    elif k in ["writable", "writeable"]: current["writable"] = "Yes" if v.lower() == "yes" else "No"
                    elif k == "browseable": current["browseable"] = "Yes" if v.lower() == "yes" else "No"
                    elif k == "valid users": current["valid_users"] = v
                    elif k == "create mask": current["create_mask"] = v
                    elif k == "directory mask": current["directory_mask"] = v
        shares.append(current)
    return shares

def control_samba(action: str):
    if action in ['start', 'stop', 'restart']:
        # Coba Arch dulu
        res = subprocess.run(["sudo", "systemctl", action, "smb", "nmb"], check=False)
        # Kalau gagal/gak ada, fallback ke Debian/Ubuntu
        if res.returncode != 0:
            subprocess.run(["sudo", "systemctl", action, "smbd", "nmbd"], check=False)

def get_samba_logs():
    try:
        # Coba Arch dulu
        res = subprocess.run(["sudo", "journalctl", "-u", "smb", "-n", "100", "--no-pager"], capture_output=True, text=True)
        if res.returncode != 0:
            # Fallback ke Debian
            res = subprocess.run(["sudo", "journalctl", "-u", "smbd", "-n", "100", "--no-pager"], capture_output=True, text=True)
        return res.stdout
    except Exception as e:
        return str(e)

def manage_smb_include(share_name: str, action: str):
    conf_path = "/etc/samba/smb.conf"
    include_line = f"include = {SHARE_CONF_DIR}/{share_name}.conf"
    
    try:
        with open(conf_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    if action == 'add':
        # Hapus wildcard include lama jika masih ada
        lines = [l for l in lines if "include = /etc/samba/shares.conf.d/*.conf" not in l]
        # Masukkan include spesifik jika belum ada
        if not any(include_line in l for l in lines):
            lines.append(f"{include_line}\n")
    elif action == 'remove':
        lines = [l for l in lines if include_line not in l]

    with open(conf_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
def save_samba_share(name, path, guest_ok, writable, browseable, valid_users, create_mask, directory_mask, raw_config):
    import os
    os.makedirs(SHARE_CONF_DIR, exist_ok=True)
    conf_path = f"{SHARE_CONF_DIR}/{name}.conf"
    
    if raw_config and raw_config.strip():
        content = raw_config
    else:
        guest_val = "yes" if guest_ok else "no"
        write_val = "yes" if writable else "no"
        browse_val = "yes" if browseable else "no"
        
        content = f"[{name}]\n    path = {path}\n    public = {guest_val}\n    guest ok = {guest_val}\n    writable = {write_val}\n    browseable = {browse_val}\n"
        if create_mask: content += f"    create mask = {create_mask}\n"
        if directory_mask: content += f"    directory mask = {directory_mask}\n"
        if valid_users: 
            content += f"    valid users = {valid_users}\n"
        else:
            if not guest_ok: content += f"    force user = root\n"
            
    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
        
    # Tambahkan baris include ke smb.conf
    manage_smb_include(name, 'add')
    control_samba("restart")

def delete_samba_share(name: str):
    conf_path = f"{SHARE_CONF_DIR}/{name}.conf"
    if os.path.exists(conf_path):
        os.remove(conf_path)
    # Hapus baris include dari smb.conf
    manage_smb_include(name, 'remove')
    control_samba("restart")

def set_samba_password(username: str, password: str):
    try:
        # Bikin user OS (nologin) kalau belum ada (opsional, tergantung setup lu)
        subprocess.run(["sudo", "useradd", "-M", "-s", "/sbin/nologin", username], check=False)
        # Set password Samba via smbpasswd
        proc = subprocess.Popen(["sudo", "smbpasswd", "-s", "-a", username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        proc.communicate(input=f"{password}\n{password}\n")
    except Exception as e:
        pass

def get_samba_users():
    import subprocess
    try:
        res = subprocess.run(["sudo", "pdbedit", "-L"], capture_output=True, text=True)
        users = []
        for line in res.stdout.splitlines():
            if ":" in line:
                users.append(line.split(":")[0])
        return users
    except Exception:
        return []

def delete_samba_user(username: str):
    import subprocess
    subprocess.run(["sudo", "smbpasswd", "-x", username], check=False)