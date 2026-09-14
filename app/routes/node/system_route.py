from fastapi.responses import JSONResponse
from app.services import node
from . import router


@router.get("/api/status")
async def api_status():
    deps = node.check_dependencies()
    projects = node.load_projects()
    return {"deps": deps, "projects": projects}


@router.post("/api/install")
async def api_install():
    res = node.install_dependencies()
    return JSONResponse(res)


@router.post("/api/uninstall")
async def api_uninstall():
    res = node.uninstall_dependencies()
    return JSONResponse(res)
