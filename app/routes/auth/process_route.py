from fastapi import Request, Form, responses, status

from app.services.pam import verify_linux_user

from . import router, templates


@router.post("/login")
async def login_process(
    request: Request, username: str = Form(...), password: str = Form(...)
):

    if not verify_linux_user(username, password):

        return templates.TemplateResponse(
            request=request,
            name="pages/login.html",
            context={"request": request, "error": "Check your Username or Password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["user"] = username

    return responses.RedirectResponse(
        url="/dashboard", status_code=status.HTTP_303_SEE_OTHER
    )
