from fastapi import APIRouter, Request, Form, Depends, responses, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from app.core.security import verify_session
from app.services import cloudflared_service
import subprocess

router = APIRouter(prefix="/cloudflared", tags=["Cloudflared"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def cloudflared_page(request: Request, user: str = Depends(verify_session)):
    cf_status = cloudflared_service.get_cloudflared_status()
    return templates.TemplateResponse(
        request=request,
        name="pages/cloudflared.html",
        context={
        "user": user,
        "status": cf_status,
        "active_page": "cloudflared"
    })

@router.post("/connect")
async def connect_tunnel(token: str = Form(...), _ : str = Depends(verify_session)):
    cloudflared_service.set_cloudflared_token(token)
    return responses.RedirectResponse(url="/cloudflared", status_code=303)

@router.post("/api/tunnels")
async def api_get_tunnels(payload: dict = Body(...), _ : str = Depends(verify_session)):
    api_token = payload.get("api_token")
    if not api_token:
        return JSONResponse({"status": "error", "message": "API Token kosong"})
    
    # Fungsi ini udah lu bikin di service
    result = cloudflared_service.fetch_cf_tunnels(api_token)
    return JSONResponse(result)

@router.get("/api/logs")
async def api_get_logs(_ : str = Depends(verify_session)):
    try:
        # Ambil 50 baris terakhir dari journalctl
        res = subprocess.run(
            ["sudo", "journalctl", "-u", "cloudflared", "-n", "50", "--no-pager"], 
            capture_output=True, text=True
        )
        return JSONResponse({"status": "success", "logs": res.stdout})
    except Exception as e:
        return JSONResponse({"status": "error", "logs": str(e)})

@router.post("/api/action")
async def api_action_service(payload: dict = Body(...), _ : str = Depends(verify_session)):
    action = payload.get("action")
    if action == "start":
        res = cloudflared_service.start_cloudflared()
    elif action == "stop":
        res = cloudflared_service.stop_cloudflared()
    else:
        res = {"status": "error", "message": "Aksi tidak valid"}
    return JSONResponse(res)

@router.get("/api/logs")
async def api_get_logs(_ : str = Depends(verify_session)):
    try:
        res = subprocess.run(
            ["sudo", "journalctl", "-u", "cloudflared", "-n", "50", "--no-pager"], 
            capture_output=True, text=True
        )
        return JSONResponse({"status": "success", "logs": res.stdout})
    except Exception as e:
        return JSONResponse({"status": "error", "logs": str(e)})