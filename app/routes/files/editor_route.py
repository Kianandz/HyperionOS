from fastapi import Form, Depends
from fastapi.responses import JSONResponse
from app.core.security import verify_session
from app.services import files as fm_svc
from . import router


@router.get("/api/read-file")
async def api_read_file(path: str, _: str = Depends(verify_session)):
    return JSONResponse(content=fm_svc.read_file(path))


@router.post("/api/write-file")
async def api_write_file(
    path: str = Form(...), content: str = Form(...), _: str = Depends(verify_session)
):
    return JSONResponse(content=fm_svc.write_file(path, content))
