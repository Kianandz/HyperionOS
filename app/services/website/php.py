import os
import subprocess
from .constants import PHP_INI_PATHS


def get_active_php_socket():
    possible_sockets = [
        "/run/php/php*.sock",
        "/run/php-fpm/php*.sock",
        "/var/run/php/php*.sock",
        "/var/run/php-fpm/php*.sock",
    ]
    for sock in possible_sockets:
        matched_sockets = glob.glob(sock)
        if matched_sockets:
            return matched_sockets[0]

    return "/run/php-fpm/php-fpm.sock"


def has_php_files(root_dir: str) -> bool:
    if not os.path.exists(root_dir):
        return False
    try:
        for file in os.listdir(root_dir):
            if file.endswith(".php"):
                return True
    except Exception:
        pass
    return False


def control_php_fpm(action: str):
    allowed = ["reload", "restart", "start", "stop"]
    if action not in allowed:
        raise Exception("Action is not valid")

    svc = "php-fpm"
    chk = subprocess.run(
        ["systemctl", "status", "php-fpm"], capture_output=True, text=True
    )

    if chk.returncode == 4:
        for v in ["php8.4-fpm", "php8.3-fpm", "php8.2-fpm", "php8.1-fpm", "php-fpm"]:
            check_v = subprocess.run(
                ["systemctl", "status", v], capture_output=True, text=True
            )
            if check_v.returncode != 4:
                svc = v
                break

    try:
        subprocess.run(
            ["sudo", "systemctl", action, svc],
            check=True,
            capture_output=True,
            text=True,
        )
        return {"status": "success", "message": f"PHP-FPM ({svc}) : {action}!"}
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed {action} PHP-FPM: {e.stderr or e.stdout}")


def get_php_ini_path():
    for p in PHP_INI_PATHS:
        if os.path.exists(p):
            return p
    raise Exception("php.ini not found!")


def read_php_config():
    path = get_php_ini_path()
    with open(path, "r") as f:
        return {"path": path, "config": f.read()}


def save_php_config(content: str):
    path = get_php_ini_path()
    try:
        with open(path, "w") as f:
            f.write(content)
        control_php_fpm("reload")
        return {"status": "success", "message": "Config php.ini saved!"}
    except Exception as e:
        raise Exception(f"Failed to save php.ini: {str(e)}")
