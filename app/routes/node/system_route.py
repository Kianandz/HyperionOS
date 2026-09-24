import json
from fastapi.responses import JSONResponse
from app.services import node
from . import router


@router.get("/api/status")
async def api_status():
    deps = node.check_dependencies()
    projects = node.load_projects()

    pm2_res = node.run_cmd("sudo pm2 jlist")
    if pm2_res["success"]:
        try:
            pm2_data = json.loads(pm2_res["output"])
            pm2_status_map = {app["name"]: app["pm2_env"]["status"] for app in pm2_data}

            for p in projects:
                p["status"] = pm2_status_map.get(p["name"], "stopped/missing")
        except Exception:
            pass

    return {"deps": deps, "projects": projects}


@router.post("/api/install")
async def api_install():
    res = node.install_dependencies()
    return JSONResponse(res)


@router.post("/api/uninstall")
async def api_uninstall():
    res = node.uninstall_dependencies()
    return JSONResponse(res)
