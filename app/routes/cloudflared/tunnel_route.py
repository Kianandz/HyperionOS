from fastapi import Form, Depends, Body, responses
from fastapi.responses import JSONResponse
from app.core.security import verify_session
from app.services import cloudflared as cloudflared_service
from . import router


@router.post("/connect")
async def connect_tunnel(token: str = Form(...), _: str = Depends(verify_session)):
    cloudflared_service.set_cloudflared_token(token)
    return responses.RedirectResponse(url="/cloudflared", status_code=303)


@router.post("/api/tunnels")
async def api_get_tunnels(payload: dict = Body(...), _: str = Depends(verify_session)):
    api_token = payload.get("api_token")
    if not api_token:
        return JSONResponse({"status": "error", "message": "API Token empty!"})

    result = cloudflared_service.fetch_cf_tunnels(api_token)
    return JSONResponse(result)
