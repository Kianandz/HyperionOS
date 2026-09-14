from fastapi import Request, Depends
from app.core.security import verify_session
from . import router, templates


@router.get("")
async def terminal_page(request: Request, user: str = Depends(verify_session)):
    return templates.TemplateResponse(
        request=request,
        name="pages/terminal.html",
        context={"user": user, "active_page": "terminal"},
    )
