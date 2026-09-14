from fastapi import APIRouter

from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Auth"])


templates = Jinja2Templates(directory="app/templates")


from . import page_route, process_route, logout_route
