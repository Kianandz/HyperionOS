from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services import database as db_svc
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def databases_page(request: Request, user: str = Depends(verify_session)):
    mysql_installed = db_svc.check_mysql_installed()
    return templates.TemplateResponse(
        request=request,
        name="pages/databases.html",
        context={
            "user": user,
            "active_page": "databases",
            "mysql_installed": mysql_installed,
        },
    )


@router.post("/install-local", response_class=responses.HTMLResponse)
async def install_mysql(user: str = Depends(verify_session)):
    res = db_svc.install_local_mysql()
    color = "emerald" if res["status"] == "success" else "red"
    return f'<div class="p-3 bg-{color}-500/10 border border-{color}-500/20 text-{color}-400 rounded-lg text-xs">{res["message"]}</div>'
