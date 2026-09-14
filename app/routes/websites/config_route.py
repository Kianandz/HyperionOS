from fastapi import Depends
from fastapi.responses import JSONResponse
from app.core.security import verify_session
from app.services import website
from . import router


@router.get("/config/{domain}")
async def get_config(domain: str, _: str = Depends(verify_session)):
    try:
        raw_conf = website.get_website_config(domain)
        return JSONResponse({"status": "success", "config": raw_conf})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=404)
