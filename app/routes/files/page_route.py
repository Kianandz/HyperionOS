from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services import files as fm_svc
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def files_page(
    request: Request, path: str = "", user: str = Depends(verify_session)
):
    contents = fm_svc.get_directory_contents(path)
    return templates.TemplateResponse(
        request=request,
        name="pages/files.html",
        context={"user": user, "contents": contents, "active_page": "files"},
    )
