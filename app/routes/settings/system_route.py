from fastapi import Form, Depends, responses
from app.core.security import verify_session
from . import router
from app.services.settings import system_service


@router.post("/dns")
async def save_dns(
    primary: str = Form("1.1.1.1"),
    secondary: str = Form("8.8.8.8"),
    _: str = Depends(verify_session),
):
    system_service.update_resolv_conf(primary, secondary)
    return responses.RedirectResponse(url="/settings", status_code=303)


@router.post("/clean-logs")
async def clean_logs(_: str = Depends(verify_session)):
    system_service.vacuum_journal_logs()
    return responses.RedirectResponse(url="/settings", status_code=303)


@router.post("/network/apply")
async def apply_network(
    interface: str = Form(...),
    mode: str = Form(...),
    ip_address: str = Form(""),
    gateway: str = Form(""),
    _: str = Depends(verify_session),
):
    system_service.apply_network_config(interface, mode, ip_address, gateway)
    return responses.RedirectResponse(url="/settings", status_code=303)


@router.post("/timezone")
async def save_timezone(
    timezone: str = Form(...), ntp: str = Form("off"), _: str = Depends(verify_session)
):
    system_service.apply_time_config(timezone, ntp)
    return responses.RedirectResponse(url="/settings", status_code=303)


@router.post("/password")
async def save_password(
    username: str = Form(...),
    password: str = Form(...),
    _: str = Depends(verify_session),
):
    system_service.change_user_password(username, password)
    return responses.RedirectResponse(url="/settings", status_code=303)


@router.post("/port")
async def save_port(port: str = Form(...), _: str = Depends(verify_session)):
    if port.isdigit():
        system_service.update_app_port(port)
    return responses.RedirectResponse(url="/settings", status_code=303)
