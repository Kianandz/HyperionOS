from fastapi import Request, responses, status

from . import router, templates


@router.get("/login", response_class=responses.HTMLResponse)
async def login_page(request: Request):

    if request.session.get("user"):

        return responses.RedirectResponse(
            url="/dashboard", status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        request=request,
        name="pages/login.html",
        context={"request": request, "error": None},
    )
