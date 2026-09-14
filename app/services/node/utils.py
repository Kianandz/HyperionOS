import subprocess
import shutil
import json
from .config import PROJECTS_CONFIG


def run_cmd(cmd):
    try:
        res = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return {"success": True, "output": res.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}


def get_pkg_manager():
    if shutil.which("apt"):
        return "apt"
    elif shutil.which("pacman"):
        return "pacman"
    return "unknown"


def load_projects():
    if not PROJECTS_CONFIG.exists():
        PROJECTS_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        PROJECTS_CONFIG.write_text("[]")
    return json.loads(PROJECTS_CONFIG.read_text())


def save_projects(projects):
    PROJECTS_CONFIG.write_text(json.dumps(projects, indent=2))
