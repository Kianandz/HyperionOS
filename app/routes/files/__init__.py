from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/files", tags=["Files"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, crud_route, transfer_route, archive_route, editor_route
