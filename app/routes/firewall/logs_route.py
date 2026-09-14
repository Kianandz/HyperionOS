from fastapi import Depends, responses
from app.core.security import verify_session
from app.services import ufw as ufw_service
from . import router


@router.get("/logs", response_class=responses.JSONResponse)
async def get_firewall_logs(user: str = Depends(verify_session)):
    logs_data = ufw_service.get_ufw_logs(lines=50)
    return responses.JSONResponse(content=logs_data)
