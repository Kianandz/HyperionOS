import subprocess
import os
import psutil
from . import system_service, upload_service


def get_settings_context() -> dict:
    ssh_check = subprocess.run(
        ["systemctl", "is-active", "ssh"], capture_output=True, text=True
    )
    ssh_active = ssh_check.stdout.strip() == "active"
    swap = psutil.swap_memory()

    sys_status = {
        "hostname": os.uname().nodename,
        "kernel": os.uname().release,
        "ssh_active": ssh_active,
        "swap_total_mb": round(swap.total / (1024 * 1024), 2),
        "swap_used_mb": round(swap.used / (1024 * 1024), 2),
        "swap_percent": swap.percent,
    }

    return {
        "sys_status": sys_status,
        "network": system_service.get_network_info(),
        "backgrounds": upload_service.list_backgrounds(),
        "time_info": system_service.get_time_info(),     # BARU
        "system_users": system_service.get_system_users(), # BARU
        "app_port": system_service.get_app_port(),         # BARU
    }