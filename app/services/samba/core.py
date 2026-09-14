import os
import subprocess
from .config import SHARE_CONF_DIR


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
    # Load all individual configs from shares folder
    include = {SHARE_CONF_DIR}/*.conf
"""
        with open(conf_path, "w", encoding="utf-8") as f:
            f.write(default_smb)


def control_samba(action: str):
    if action in ["start", "stop", "restart"]:
        res = subprocess.run(["sudo", "systemctl", action, "smb", "nmb"], check=False)
        if res.returncode != 0:
            subprocess.run(["sudo", "systemctl", action, "smbd", "nmbd"], check=False)


def get_samba_logs():
    try:
        res = subprocess.run(
            ["sudo", "journalctl", "-u", "smb", "-n", "100", "--no-pager"],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            res = subprocess.run(
                ["sudo", "journalctl", "-u", "smbd", "-n", "100", "--no-pager"],
                capture_output=True,
                text=True,
            )
        return res.stdout
    except Exception as e:
        return str(e)
