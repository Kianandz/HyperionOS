from fastapi import Form, Depends, responses
from fastapi.responses import JSONResponse
from app.core.security import verify_session
from app.services import samba as smb_svc
from . import router


@router.post("/user")
async def samba_manage_user(
    username: str = Form(...),
    password: str = Form(...),
    _: str = Depends(verify_session),
):
    smb_svc.set_samba_password(username, password)
    return responses.RedirectResponse(url="/files/samba", status_code=303)


@router.get("/api/users")
async def get_samba_users(_: str = Depends(verify_session)):
    return JSONResponse(
        content={"status": "success", "users": smb_svc.get_samba_users()}
    )


@router.post("/user/delete")
async def samba_delete_user(
    username: str = Form(...), _: str = Depends(verify_session)
):
    smb_svc.delete_samba_user(username)
    return responses.RedirectResponse(url="/files/samba", status_code=303)
