from fastapi import Request, Depends, responses
from app.core.security import verify_session
import subprocess
import os
import psutil
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def settings_page(request: Request, user: str = Depends(verify_session)):
    ssh_check = subprocess.run(
        ["systemctl", "is-active", "ssh"], capture_output=True, text=True
    )
    ssh_active = ssh_check.stdout.strip() == "active"
    swap = psutil.swap_memory()

    status_data = {
        "hostname": os.uname().nodename,
        "kernel": os.uname().release,
        "ssh_active": ssh_active,
        "swap_total_mb": round(swap.total / (1024 * 1024), 2),
        "swap_used_mb": round(swap.used / (1024 * 1024), 2),
        "swap_percent": swap.percent,
    }

    return templates.TemplateResponse(
        request=request,
        name="pages/settings.html",
        context={"user": user, "sys_status": status_data, "active_page": "settings"},
    )
