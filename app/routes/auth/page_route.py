from fastapi import Request, responses, status
import random

from . import router, templates
from .process_route import login_attempts

@router.get("/login", response_class=responses.HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user"):
        return responses.RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    client_ip = request.client.host if request.client else "Unknown IP"
    attempt = login_attempts.get(client_ip, {"count": 0})
    
    show_captcha = attempt.get("count", 0) >= 3
    
    if show_captcha and not request.session.get("captcha_question"):
        num1, num2 = random.randint(1, 9), random.randint(1, 9)
        request.session["captcha_answer"] = num1 + num2
        request.session["captcha_question"] = f"{num1} + {num2}"

    return templates.TemplateResponse(
        request=request,
        name="pages/login.html",
        context={
            "request": request, 
            "error": None,
            "show_captcha": show_captcha,
            "captcha_question": request.session.get("captcha_question", "") if show_captcha else ""
        },
    )