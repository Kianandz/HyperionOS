from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services.metrics import get_system_metrics

from . import router, templates


@router.get("/metrics-partial", response_class=responses.HTMLResponse)
async def dashboard_metrics_partial(request: Request, _: str = Depends(verify_session)):
    metrics = get_system_metrics()

    return templates.TemplateResponse(
        request=request,
        name="components/metrics_grid.html",
        context={"request": request, "metrics": metrics},
    )
