from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/docker", tags=["Docker"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, container_route, compose_route, app_route, terminal_route
