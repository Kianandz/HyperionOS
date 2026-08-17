from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ufw_service import get_ufw_status, ufw_action

router = APIRouter()

class UFWRequestSchema(BaseModel):

    command_type: str

    port: str = ""

    proto: str = "tcp"

    action: str = "allow"

@router.get("/status")
def get_status():

    return get_ufw_status()

@router.post("/manage")
def manage_ufw(data: UFWRequestSchema):

    res = ufw_action(data.command_type, data.port, data.proto, data.action)

    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    
    return res