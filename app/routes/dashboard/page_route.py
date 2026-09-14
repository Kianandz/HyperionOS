from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services.metrics import get_system_metrics

from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def dashboard_page(request: Request, user: str = Depends(verify_session)):
    metrics = get_system_metrics()

    return templates.TemplateResponse(
        request=request,
        name="pages/dashboard.html",
        context={
            "request": request,
            "user": user,
            "metrics": metrics,
            "active_page": "dashboard",
        },
    )
