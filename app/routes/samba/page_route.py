import subprocess
from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services import samba as smb_svc
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def samba_page(request: Request, user: str = Depends(verify_session)):
    shares = smb_svc.parse_smb_conf()
    try:
        st = subprocess.run(
            ["systemctl", "is-active", "smb"], capture_output=True, text=True
        ).stdout.strip()
        if st != "active":
            st = subprocess.run(
                ["systemctl", "is-active", "smbd"], capture_output=True, text=True
            ).stdout.strip()
        is_active = st == "active"
    except:
        is_active = False

    return templates.TemplateResponse(
        request=request,
        name="pages/samba.html",
        context={
            "user": user,
            "active_page": "samba",
            "shares": shares,
            "is_active": is_active,
        },
    )
