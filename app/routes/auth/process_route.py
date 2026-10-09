from fastapi import Request, Form, responses, status
from datetime import datetime, timedelta
import random

from app.services.pam import verify_linux_user
from app.services.pam.logger import logger
from . import router, templates

login_attempts = {}

@router.post("/login")
async def login_process(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...),
    captcha_answer: str = Form(None)
):
    client_ip = request.client.host if request.client else "Unknown IP"
    user_agent = request.headers.get("user-agent", "Unknown Device")

    attempt = login_attempts.get(client_ip, {"count": 0, "blocked_until": None})

    if attempt["blocked_until"] and datetime.now() < attempt["blocked_until"]:
        return templates.TemplateResponse(
            request=request,
            name="pages/login.html",
            context={"request": request, "error": "Too many failed attempts. Your IP has been temporarily blocked."},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if attempt["count"] >= 3:
        expected_captcha = request.session.get("captcha_answer")
        if not captcha_answer or str(captcha_answer) != str(expected_captcha):
            return templates.TemplateResponse(
                request=request,
                name="pages/login.html",
                context={
                    "request": request, 
                    "error": "Invalid captcha response.",
                    "show_captcha": True,
                    "captcha_question": request.session.get("captcha_question")
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    if not verify_linux_user(username, password):
        attempt["count"] += 1
        
        if attempt["count"] >= 6:
            attempt["blocked_until"] = datetime.now() + timedelta(minutes=15)
            error_msg = "Too many failed attempts. Your IP has been temporarily blocked."
            logger.warning(f"IP BLOCKED - User: '{username}' | IP: {client_ip}")
        else:
            error_msg = "Invalid username or password."
            logger.warning(f"FAILED LOGIN - User: '{username}' | IP: {client_ip} | Attempt: {attempt['count']}")

        login_attempts[client_ip] = attempt

        show_captcha = attempt["count"] >= 3
        if show_captcha:
            num1, num2 = random.randint(1, 9), random.randint(1, 9)
            request.session["captcha_answer"] = num1 + num2
            request.session["captcha_question"] = f"{num1} + {num2}"

        return templates.TemplateResponse(
            request=request,
            name="pages/login.html",
            context={
                "request": request, 
                "error": error_msg,
                "show_captcha": show_captcha,
                "captcha_question": request.session.get("captcha_question", "")
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    logger.info(f"SUCCESS LOGIN - User: '{username}' | IP: {client_ip} | Device: {user_agent}")
    login_attempts.pop(client_ip, None)
    
    request.session["user"] = username

    return responses.RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)