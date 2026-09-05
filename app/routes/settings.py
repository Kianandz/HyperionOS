from fastapi import APIRouter, Request, Form, Depends, responses, UploadFile, File
from fastapi.templating import Jinja2Templates
from app.core.security import verify_session
import subprocess
import os
import shutil
import psutil

router = APIRouter(prefix="/settings", tags=["Settings"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def settings_page(request: Request, user: str = Depends(verify_session)):
    ssh_check = subprocess.run(["systemctl", "is-active", "ssh"], capture_output=True, text=True)
    ssh_active = ssh_check.stdout.strip() == "active"
    swap = psutil.swap_memory()

    status_data = {
        "hostname": os.uname().nodename,
        "kernel": os.uname().release,
        "ssh_active": ssh_active,
        "swap_total_mb": round(swap.total / (1024 * 1024), 2),
        "swap_used_mb": round(swap.used / (1024 * 1024), 2),
        "swap_percent": swap.percent
    }

    return templates.TemplateResponse(
        request=request,
        name="pages/settings.html",
        context={
        "user": user,
        "sys_status": status_data,
        "active_page": "settings"
    })

@router.post("/dns")
async def save_dns(primary: str = Form("1.1.1.1"), secondary: str = Form("8.8.8.8"), _ : str = Depends(verify_session)):
    resolv_content = f"nameserver {primary}\nnameserver {secondary}\n"
    p = subprocess.Popen(["sudo", "tee", "/etc/resolv.conf"], stdin=subprocess.PIPE, text=True)
    p.communicate(input=resolv_content)
    return responses.RedirectResponse(url="/settings", status_code=303)

@router.post("/clean-logs")
async def clean_logs(_ : str = Depends(verify_session)):
    subprocess.run(["sudo", "journalctl", "--vacuum-size=50M"], check=True)
    return responses.RedirectResponse(url="/settings", status_code=303)

@router.post("/upload-bg")
async def upload_background(file: UploadFile = File(...), _ : str = Depends(verify_session)):
    # Buat direktori jika belum ada
    upload_dir = "app/static/uploads/backgrounds"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{file.filename}"
    
    # Simpan file secara lokal
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Ubah key 'url' jadi 'file_url' biar pas ditangkep sama frontend
    return {"status": "success", "file_url": f"/static/uploads/backgrounds/{file.filename}"}