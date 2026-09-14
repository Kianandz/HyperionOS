from fastapi import Form, Depends, responses
from app.core.security import verify_session
import subprocess
from . import router


@router.post("/dns")
async def save_dns(
    primary: str = Form("1.1.1.1"),
    secondary: str = Form("8.8.8.8"),
    _: str = Depends(verify_session),
):
    resolv_content = f"nameserver {primary}\nnameserver {secondary}\n"
    p = subprocess.Popen(
        ["sudo", "tee", "/etc/resolv.conf"], stdin=subprocess.PIPE, text=True
    )
    p.communicate(input=resolv_content)
    return responses.RedirectResponse(url="/settings", status_code=303)


@router.post("/clean-logs")
async def clean_logs(_: str = Depends(verify_session)):
    subprocess.run(["sudo", "journalctl", "--vacuum-size=50M"], check=True)
    return responses.RedirectResponse(url="/settings", status_code=303)
