from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route
from . import metrics_route
