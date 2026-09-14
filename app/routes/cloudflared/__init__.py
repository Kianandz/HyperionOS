from fastapi import APIRouter

from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/cloudflared", tags=["Cloudflared"])

templates = Jinja2Templates(directory="app/templates")


from . import page_route, tunnel_route, service_route
