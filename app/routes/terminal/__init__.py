from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/terminal", tags=["Terminal"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, ws_route
