from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import samba as smb_svc
from . import router


@router.post("/save")
async def samba_save(
    name: str = Form(...),
    path: str = Form(""),
    guest_ok: bool = Form(False),
    writable: bool = Form(False),
    browseable: bool = Form(True),
    valid_users: str = Form(""),
    create_mask: str = Form("0755"),
    directory_mask: str = Form("0755"),
    raw_config: str = Form(""),
    _: str = Depends(verify_session),
):
    smb_svc.save_samba_share(
        name,
        path,
        guest_ok,
        writable,
        browseable,
        valid_users,
        create_mask,
        directory_mask,
        raw_config,
    )
    return responses.RedirectResponse(url="/files/samba", status_code=303)


@router.post("/delete")
async def samba_delete(name: str = Form(...), _: str = Depends(verify_session)):
    smb_svc.delete_samba_share(name)
    return responses.RedirectResponse(url="/files/samba", status_code=303)
