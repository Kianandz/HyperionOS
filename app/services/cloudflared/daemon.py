import subprocess
from .constants import CLOUDFLARED_SERVICE_NAME


def set_cloudflared_token(token: str):
    try:
        subprocess.run(
            ["sudo", "cloudflared", "service", "uninstall"], capture_output=True
        )
        res = subprocess.run(
            ["sudo", "cloudflared", "service", "install", token],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            return {
                "status": "error",
                "message": res.stderr.strip() or res.stdout.strip(),
            }
        return {"status": "success", "message": "Cloudflared Tunnel connected!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_cloudflared_status():
    try:
        res = subprocess.run(
            ["sudo", "systemctl", "is-active", CLOUDFLARED_SERVICE_NAME],
            capture_output=True,
            text=True,
        )
        active = res.stdout.strip() == "active"
        return {"status": "active" if active else "inactive"}
    except Exception as e:
        return {"status": "inactive", "error": str(e)}


def start_cloudflared():
    try:
        subprocess.run(
            ["sudo", "systemctl", "start", CLOUDFLARED_SERVICE_NAME], check=True
        )
        return {"status": "success", "message": "Cloudflared successfully started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def stop_cloudflared():
    try:
        subprocess.run(
            ["sudo", "systemctl", "stop", CLOUDFLARED_SERVICE_NAME], check=True
        )
        return {"status": "success", "message": "Cloudflared successfully stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
