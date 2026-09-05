from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from app.core.config import settings
from app.routes import auth, dashboard, websites, database, docker, firewall, files, cloudflared, settings as settings_route

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="hyperion_session",
    max_age=3600 * 24
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def custom_401_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/dashboard")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(websites.router)
app.include_router(database.router)
app.include_router(docker.router)
app.include_router(firewall.router)
app.include_router(files.router)
app.include_router(cloudflared.router)
app.include_router(settings_route.router)

load_dotenv()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)