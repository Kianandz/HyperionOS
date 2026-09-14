from fastapi import Form
from fastapi.responses import JSONResponse
from app.services import node
from . import router


@router.post("/api/add")
async def api_add(
    name: str = Form(...),
    source_type: str = Form(...),
    source_val: str = Form(""),
    env_content: str = Form(""),
    start_cmd: str = Form(...),
):
    res = node.add_project(name, source_type, source_val, env_content, start_cmd)
    return JSONResponse(res)


@router.post("/api/delete")
async def api_delete(name: str = Form(...)):
    res = node.delete_project(name)
    return JSONResponse(res)


@router.post("/api/modify")
async def api_modify(
    name: str = Form(...), pkg_action: str = Form(""), start_cmd: str = Form(...)
):
    projects = node.load_projects()
    proj = next((p for p in projects if p["name"] == name), None)
    if not proj:
        return JSONResponse({"success": False, "error": "Project not found"})

    proj_path = proj["path"]
    if pkg_action:
        node.run_cmd(f"cd {proj_path} && npm i {pkg_action}")

    node.run_cmd(f"pm2 restart {name} --update-env")
    return JSONResponse({"success": True})
