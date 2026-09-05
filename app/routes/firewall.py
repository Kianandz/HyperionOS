from fastapi import APIRouter, Request, Form, Depends, responses
from fastapi.templating import Jinja2Templates
from app.core.security import verify_session
from app.services import ufw_service

router = APIRouter(prefix="/firewall", tags=["Firewall"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def firewall_page(request: Request, user: str = Depends(verify_session)):
    ufw_data = ufw_service.get_ufw_status()
    return templates.TemplateResponse(
        request=request,
        name="pages/firewall.html",
        context={
            "user": user,
            "ufw": ufw_data,
            "active_page": "firewall"
        }
    )

# Endpoint khusus buat refresh tabel via HTMX
@router.get("/table", response_class=responses.HTMLResponse)
async def firewall_table(request: Request, user: str = Depends(verify_session)):
    ufw_data = ufw_service.get_ufw_status()
    return templates.TemplateResponse(
        request=request,
        name="components/firewall/rules_table.html",
        context={"ufw": ufw_data}
    )

@router.post("/action")
async def firewall_action(
    command_type: str = Form(...),
    port: str = Form(""),
    proto: str = Form("tcp"),
    action: str = Form("allow"),
    direction: str = Form("incoming"),
    _ : str = Depends(verify_session)
):
    result = ufw_service.ufw_action(command_type, port, proto, action, direction)
    if result["status"] == "error":
        return responses.JSONResponse(content=result, status_code=400)
    return responses.JSONResponse(content=result)

@router.get("/logs", response_class=responses.JSONResponse)
async def get_firewall_logs(user: str = Depends(verify_session)):
    logs_data = ufw_service.get_ufw_logs(lines=50)
    return responses.JSONResponse(content=logs_data)