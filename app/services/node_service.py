import os
import subprocess
import shutil
import json
from pathlib import Path

PROJECTS_CONFIG = Path("app/storage/node_projects.json")

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {"success": True, "output": res.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}

def get_pkg_manager():
    if shutil.which("apt"):
        return "apt"
    elif shutil.which("pacman"):
        return "pacman"
    return "unknown"

def check_dependencies():
    return {
        "node": shutil.which("node") is not None,
        "npm": shutil.which("npm") is not None,
        "pm2": shutil.which("pm2") is not None,
        "manager": get_pkg_manager()
    }

def install_dependencies():
    mgr = get_pkg_manager()
    if mgr == "apt":
        cmd = "export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y nodejs npm && npm install -g pm2"
    elif mgr == "pacman":
        cmd = "pacman -Sy --noconfirm nodejs npm && npm install -g pm2"
    else:
        return {"success": False, "error": "Unsupported package manager (not Debian/Arch based)."}
    return run_cmd(cmd)

def uninstall_dependencies():
    mgr = get_pkg_manager()
    if mgr == "apt":
        cmd = "apt-get remove -y nodejs npm && npm uninstall -g pm2"
    elif mgr == "pacman":
        cmd = "pacman -R --noconfirm nodejs npm && npm uninstall -g pm2"
    else:
        return {"success": False, "error": "Unsupported package manager."}
    return run_cmd(cmd)

def load_projects():
    if not PROJECTS_CONFIG.exists():
        PROJECTS_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        PROJECTS_CONFIG.write_text("[]")
    return json.loads(PROJECTS_CONFIG.read_text())

def save_projects(projects):
    PROJECTS_CONFIG.write_text(json.dumps(projects, indent=2))

def add_project(name, source_type, source_val, env_content, start_cmd):
    base_dir = Path("/var/www/nodes")
    base_dir.mkdir(parents=True, exist_ok=True)
    proj_dir = base_dir / name
    
    if proj_dir.exists():
        return {"success": False, "error": "Project with this name already exists."}

    if source_type == "git":
        res = run_cmd(f"git clone {source_val} {proj_dir}")
        if not res["success"]:
            return res
    elif source_type == "folder":
        # Jika upload path lokal atau extract
        if Path(source_val).exists():
            shutil.copytree(source_val, proj_dir)
        else:
            proj_dir.mkdir(parents=True, exist_ok=True)
            # Handle manual file uploads di route handler jika zip/tar

    # Hapus node_modules jika ikut ke-upload/clone
    nm_dir = proj_dir / "node_modules"
    if nm_dir.exists():
        shutil.rmtree(nm_dir)

    # Buat/Simpan .env jika ada isinya
    if env_content:
        env_path = proj_dir / ".env"
        env_path.write_text(env_content)

    # Jalankan npm i
    npm_res = run_cmd(f"cd {proj_dir} && npm install")
    if not npm_res["success"]:
        return {"success": False, "error": f"Failed running npm i: {npm_res['error']}"}

    # Jalankan dengan PM2
    pm2_res = run_cmd(f"cd {proj_dir} && pm2 start {start_cmd} --name {name}")
    if not pm2_res["success"]:
        return {"success": False, "error": f"Failed starting PM2: {pm2_res['error']}"}

    # Simpan ke config json
    projects = load_projects()
    projects.append({
        "name": name,
        "path": str(proj_dir),
        "start_cmd": start_cmd,
        "status": "online"
    })
    save_projects(projects)

    return {"success": True}

def delete_project(name):
    projects = load_projects()
    proj = next((p for p in projects if p["name"] == name), None)
    if proj:
        run_cmd(f"pm2 delete {name}")
        shutil.rmtree(proj["path"], ignore_errors=True)
        projects = [p for p in projects if p["name"] != name]
        save_projects(projects)
    return {"success": True}

def get_project_logs(name):
    res = run_cmd(f"pm2 logs {name} --lines 100 --nostream")
    return res.get("output", res.get("error", "No logs found."))