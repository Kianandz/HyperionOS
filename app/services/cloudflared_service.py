import subprocess
import os

CLOUDFLARED_SERVICE_NAME = "cloudflared"

def set_cloudflared_token(token: str):

    """Install dan jalankan cloudflared service pakai token."""

    try:

        subprocess.run(["sudo", "cloudflared", "service", "install", token], check=True)

        return {"status": "success", "message": "Cloudflared Tunnel berhasil dihubungkan!"}
    
    except Exception as e:

        return {"status": "error", "message": str(e)}
    

def get_cloudflared_status():

    """Cek apakah service cloudflared running di background."""

    try:

        res = subprocess.run(["systemctl", "is-active", CLOUDFLARED_SERVICE_NAME], capture_output=True, text=True)

        active = res.stdout.strip() == "active"

        return {"status": "active" if active else "inactive"}
    
    except Exception as e:
        
        return {"status": "inactive", "error": str(e)}