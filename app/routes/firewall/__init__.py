from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/firewall", tags=["Firewall"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, action_route, logs_route
