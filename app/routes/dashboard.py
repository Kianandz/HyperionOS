from fastapi import APIRouter, Request, Depends, responses #
from fastapi.templating import Jinja2Templates 
from app.core.security import verify_session 
from app.services.metrics import get_system_metrics 

router = APIRouter(prefix="/dashboard", tags=["Dashboard"]) 
templates = Jinja2Templates(directory="app/templates") 

# Route Full Page (Pertama kali dibuka)[cite: 3]
@router.get("", response_class=responses.HTMLResponse) 
async def dashboard_page(request: Request, user: str = Depends(verify_session)): 
    metrics = get_system_metrics() 
    
    # ✅ PERBAIKAN 1: Jabarin parameter request, name, dan context
    return templates.TemplateResponse(
        request=request,
        name="pages/dashboard.html", 
        context={
            "request": request,
            "user": user,
            "metrics": metrics,
            "active_page": "dashboard"
        }
    )

# Endpoint HTMX Polling (Return potongan HTML grid doang)[cite: 3]
@router.get("/metrics-partial", response_class=responses.HTMLResponse) 
async def dashboard_metrics_partial(request: Request, _: str = Depends(verify_session)): 
    metrics = get_system_metrics() 
    
    # ✅ PERBAIKAN 2: Jabarin juga di bagian HTMX partial-nya
    return templates.TemplateResponse(
        request=request,
        name="components/metrics_grid.html", 
        context={
            "request": request,
            "metrics": metrics
        }
    )