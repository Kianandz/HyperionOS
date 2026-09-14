from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import ufw as ufw_service
from . import router


@router.post("/action")
async def firewall_action(
    command_type: str = Form(...),
    port: str = Form(""),
    proto: str = Form("tcp"),
    action: str = Form("allow"),
    direction: str = Form("incoming"),
    _: str = Depends(verify_session),
):
    result = ufw_service.ufw_action(command_type, port, proto, action, direction)
    if result["status"] == "error":
        return responses.JSONResponse(content=result, status_code=400)
    return responses.JSONResponse(content=result)
