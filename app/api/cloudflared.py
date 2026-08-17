from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.cloudflared_service import set_cloudflared_token, get_cloudflared_status

router = APIRouter()

class TokenSchema(BaseModel):

    token: str

@router.get("/status")
def status():

    return get_cloudflared_status()

@router.post("/connect")
def connect_tunnel(data: TokenSchema):

    res = set_cloudflared_token(data.token)

    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    
    return res