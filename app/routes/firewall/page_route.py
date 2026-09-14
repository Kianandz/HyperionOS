from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services import ufw as ufw_service
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def firewall_page(request: Request, user: str = Depends(verify_session)):
    ufw_data = ufw_service.get_ufw_status()
    return templates.TemplateResponse(
        request=request,
        name="pages/firewall.html",
        context={"user": user, "ufw": ufw_data, "active_page": "firewall"},
    )


@router.get("/table", response_class=responses.HTMLResponse)
async def firewall_table(request: Request, user: str = Depends(verify_session)):
    ufw_data = ufw_service.get_ufw_status()
    return templates.TemplateResponse(
        request=request,
        name="components/firewall/rules_table.html",
        context={"ufw": ufw_data},
    )
