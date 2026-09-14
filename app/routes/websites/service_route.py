from fastapi import Depends, responses
from app.core.security import verify_session
from app.services import website
from . import router


@router.post("/control/{service}/{action}")
async def control_service(service: str, action: str, _: str = Depends(verify_session)):
    if service == "nginx":
        website.control_nginx(action)
    elif service == "php":
        website.control_php_fpm(action)
    return responses.RedirectResponse(url="/websites", status_code=303)


@router.get("/logs/{service}")
async def get_logs(service: str, _: str = Depends(verify_session)):
    logs = website.get_service_logs(service)
    return responses.PlainTextResponse(logs)
