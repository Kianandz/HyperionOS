from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/websites", tags=["Websites"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, site_route, service_route, config_route, files_route
