from fastapi import APIRouter, Request, Form, responses, status
from fastapi.templating import Jinja2Templates
from app.services.pam_service import verify_linux_user 

router = APIRouter(tags=["Auth"]) 
templates = Jinja2Templates(directory="app/templates") 

@router.get("/login", response_class=responses.HTMLResponse) 
async def login_page(request: Request): 
    if request.session.get("user"): 
        return responses.RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER) 
    
    # PERBAIKAN DI SINI: Jabarin request, name, dan context
    return templates.TemplateResponse(
        request=request, 
        name="pages/login.html", 
        context={"request": request, "error": None}
    )

@router.post("/login") 
async def login_process(request: Request, username: str = Form(...), password: str = Form(...)): 
    if not verify_linux_user(username, password): 
        # PERBAIKAN DI SINI: Sama, jabarin juga nama parameternya
        return templates.TemplateResponse(
            request=request,
            name="pages/login.html", 
            context={"request": request, "error": "Username atau Password salah!"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Simpan session di server[cite: 2]
    request.session["user"] = username 
    return responses.RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER) 

@router.get("/logout") 
async def logout(request: Request): 
    request.session.clear() 
    return responses.RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER) 