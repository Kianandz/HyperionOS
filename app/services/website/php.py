import os
import subprocess
from .constants import PHP_INI_PATHS


def get_active_php_socket():
    possible_sockets = [
        "/run/php-fpm/php-fpm.sock",
        "/run/php/php-fpm.sock",
        "/var/run/php-fpm/php-fpm.sock",
    ]
    for sock in possible_sockets:
        if os.path.exists(sock):
            return sock
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
        raise Exception("Actions is not valid")

    svc = "php-fpm"
    chk = subprocess.run(
        ["sudo", "systemctl", "status", "php-fpm"], capture_output=True, text=True
    )
    if "loaded" not in chk.stdout:
        for v in ["php8.3-fpm", "php8.2-fpm", "php8.1-fpm", "php-fpm"]:
            if (
                "loaded"
                in subprocess.run(
                    ["sudo", "systemctl", "status", v], capture_output=True, text=True
                ).stdout
            ):
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
