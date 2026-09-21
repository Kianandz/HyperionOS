from fastapi import Request, Form, responses, status

from app.services.pam import verify_linux_user

from app.services.pam.logger import logger

from . import router, templates


@router.post("/login")
async def login_process(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    client_ip = request.client.host if request.client else "Unknown IP"
    user_agent = request.headers.get("user-agent", "Unknown Device")

    if not verify_linux_user(username, password):

        logger.warning(
            f"FAILED LOGIN - User: '{username}' | IP: {client_ip} | Device: {user_agent}"
        )

        return templates.TemplateResponse(
            request=request,
            name="pages/login.html",
            context={"request": request, "error": "Check your Username or Password"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    logger.info(
        f"SUCCESS LOGIN - User: '{username}' | IP: {client_ip} | Device: {user_agent}"
    )

    request.session["user"] = username

    return responses.RedirectResponse(
        url="/dashboard", status_code=status.HTTP_303_SEE_OTHER
    )
