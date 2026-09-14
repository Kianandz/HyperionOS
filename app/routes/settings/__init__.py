from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/settings", tags=["Settings"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, system_route, upload_route
