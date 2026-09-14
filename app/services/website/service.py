import os
import subprocess


def get_service_status(service_name: str) -> dict:
    try:
        res = subprocess.run(
            ["sudo", "systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
        )
        status = res.stdout.strip()
        check_exist = subprocess.run(
            ["sudo", "systemctl", "status", service_name],
            capture_output=True,
            text=True,
        )
        is_installed = "loaded" in check_exist.stdout or "loaded" in check_exist.stderr
        return {
            "service": service_name,
            "status": status if is_installed else "not_installed",
            "is_active": status == "active",
        }
    except Exception:
        return {"service": service_name, "status": "unknown", "is_active": False}


def get_service_logs(target: str, lines: int = 150):
    possible_units = {
        "nginx": ["nginx", "nginx.service"],
        "php": [
            "php-fpm",
            "php-fpm.service",
            "php8.3-fpm",
            "php8.2-fpm",
            "php81-php-fpm",
        ],
    }
    units = possible_units.get(target, [target])

    for u in units:
        try:
            res = subprocess.run(
                ["journalctl", "-u", u, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
            )
            if (
                res.returncode == 0
                and res.stdout.strip()
                and "No entries" not in res.stdout
            ):
                return res.stdout
        except Exception:
            pass

    log_files = {
        "nginx": ["/var/log/nginx/error.log", "/var/log/nginx/access.log"],
        "php": [
            "/var/log/php-fpm/error.log",
            "/var/log/php-fpm.log",
            "/var/log/php8.3-fpm.log",
            "/var/log/php8.2-fpm.log",
        ],
    }
    target_files = log_files.get(target, [])

    for file_path in target_files:
        if os.path.exists(file_path):
            try:
                res = subprocess.run(
                    ["tail", "-n", str(lines), file_path],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0 and res.stdout.strip():
                    return f"--- File Log: {file_path} ---\n\n" + res.stdout
            except Exception:
                pass

    return f"Log {target} not found in journalctl and /var/log/."
