from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services import website
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def websites_page(request: Request, user: str = Depends(verify_session)):
    sites = website.list_websites()
    status_nginx = website.get_service_status("nginx")
    status_php = website.get_service_status("php-fpm")

    return templates.TemplateResponse(
        request=request,
        name="pages/websites.html",
        context={
            "user": user,
            "sites": sites,
            "nginx": status_nginx,
            "php_fpm": status_php,
            "active_page": "websites",
        },
    )
