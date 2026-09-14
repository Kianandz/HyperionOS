from fastapi import Request
from fastapi.responses import HTMLResponse
from . import router, templates


@router.get("", response_class=HTMLResponse)
async def node_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="pages/node.html", context={"active_page": "node"}
    )
