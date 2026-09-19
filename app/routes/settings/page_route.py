from fastapi import Request, Depends, responses
from app.core.security import verify_session
from . import router, templates
from app.services.settings import page_service

@router.get("", response_class=responses.HTMLResponse)
async def settings_page(request: Request, user: str = Depends(verify_session)):
    context_data = page_service.get_settings_context()

    return templates.TemplateResponse(
        request=request,
        name="pages/settings.html",
        context={"user": user, **context_data, "active_page": "settings"},
    )