from fastapi import Request, Depends, responses

from app.core.security import verify_session

from app.services import cloudflared as cloudflared_service

from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def cloudflared_page(request: Request, user: str = Depends(verify_session)):

    cf_status = cloudflared_service.get_cloudflared_status()

    return templates.TemplateResponse(
        request=request,
        name="pages/cloudflared.html",
        context={"user": user, "status": cf_status, "active_page": "cloudflared"},
    )
