import shutil
from .utils import get_pkg_manager, run_cmd


def check_dependencies():
    return {
        "node": shutil.which("node") is not None,
        "npm": shutil.which("npm") is not None,
        "pm2": shutil.which("pm2") is not None,
        "manager": get_pkg_manager(),
    }


def install_dependencies():
    mgr = get_pkg_manager()
    if mgr == "apt":
        cmd = "export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y nodejs npm && npm install -g pm2"
    elif mgr == "pacman":
        cmd = "sudo pacman -Sy --noconfirm ada nodejs npm && sudo npm install -g pm2"
    else:
        return {
            "success": False,
            "error": "Unsupported package manager (not Debian/Arch based).",
        }
    return run_cmd(cmd)


def uninstall_dependencies():
    mgr = get_pkg_manager()
    if mgr == "apt":
        cmd = "apt-get remove -y ada nodejs npm && sudo npm uninstall -g pm2"
    elif mgr == "pacman":
        cmd = "sudo pacman -R --noconfirm nodejs npm && sudo npm uninstall -g pm2"
    else:
        return {"success": False, "error": "Unsupported package manager."}
    return run_cmd(cmd)
