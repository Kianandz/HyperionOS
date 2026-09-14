from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/files/samba", tags=["Samba"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, service_route, share_route, user_route
