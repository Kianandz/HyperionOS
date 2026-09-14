from fastapi import Depends, responses
from fastapi.responses import JSONResponse
from app.core.security import verify_session
from app.services import samba as smb_svc
from . import router


@router.post("/control/{action}")
async def samba_control(action: str, _: str = Depends(verify_session)):
    smb_svc.control_samba(action)
    return responses.RedirectResponse(url="/files/samba", status_code=303)


@router.get("/logs")
async def samba_logs(_: str = Depends(verify_session)):
    return JSONResponse(content={"status": "success", "logs": smb_svc.get_samba_logs()})
