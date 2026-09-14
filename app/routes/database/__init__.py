from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/databases", tags=["Databases"])
templates = Jinja2Templates(directory="app/templates")

from . import page_route, db_route, table_route, row_route, query_route
