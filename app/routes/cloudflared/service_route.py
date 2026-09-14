import subprocess

from fastapi import Depends, Body

from fastapi.responses import JSONResponse

from app.core.security import verify_session

from app.services import cloudflared as cloudflared_service

from . import router


@router.post("/api/action")
async def api_action_service(
    payload: dict = Body(...), _: str = Depends(verify_session)
):

    action = payload.get("action")

    if action == "start":

        res = cloudflared_service.start_cloudflared()

    elif action == "stop":

        res = cloudflared_service.stop_cloudflared()

    else:

        res = {"status": "error", "message": "Action not valid!"}

    return JSONResponse(res)


@router.get("/api/logs")
async def api_get_logs(_: str = Depends(verify_session)):

    try:

        res = subprocess.run(
            ["sudo", "journalctl", "-u", "cloudflared", "-n", "50", "--no-pager"],
            capture_output=True,
            text=True,
        )

        return JSONResponse({"status": "success", "logs": res.stdout})

    except Exception as e:

        return JSONResponse({"status": "error", "logs": str(e)})
