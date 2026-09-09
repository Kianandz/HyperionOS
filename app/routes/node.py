from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.services import node_service
import shutil
from pathlib import Path

router = APIRouter(prefix="/websites/node", tags=["Node Websites"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def node_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/node.html",
        context={"active_page": "node"}
    )

@router.get("/api/status")
async def api_status():
    deps = node_service.check_dependencies()
    projects = node_service.load_projects()
    return {"deps": deps, "projects": projects}

@router.post("/api/install")
async def api_install():
    res = node_service.install_dependencies()
    return JSONResponse(res)

@router.post("/api/uninstall")
async def api_uninstall():
    res = node_service.uninstall_dependencies()
    return JSONResponse(res)

@router.post("/api/add")
async def api_add(
    name: str = Form(...),
    source_type: str = Form(...),
    source_val: str = Form(""),
    env_content: str = Form(""),
    start_cmd: str = Form(...)
):
    res = node_service.add_project(name, source_type, source_val, env_content, start_cmd)
    return JSONResponse(res)

@router.post("/api/delete")
async def api_delete(name: str = Form(...)):
    res = node_service.delete_project(name)
    return JSONResponse(res)

@router.get("/api/logs/{name}")
async def api_logs(name: str):
    logs = node_service.get_project_logs(name)
    return {"logs": logs}

@router.post("/api/modify")
async def api_modify(
    name: str = Form(...),
    pkg_action: str = Form(""),
    start_cmd: str = Form(...)
):
    projects = node_service.load_projects()
    proj = next((p for p in projects if p["name"] == name), None)
    if not proj:
        return JSONResponse({"success": False, "error": "Project not found"})
    
    proj_path = proj["path"]
    if pkg_action:
        # Contoh: npm i express atau npm uninstall express
        node_service.run_cmd(f"cd {proj_path} && npm i {pkg_action}")
    
    # Restart pm2 dengan command baru
    node_service.run_cmd(f"pm2 restart {name} --update-env")
    return JSONResponse({"success": True})