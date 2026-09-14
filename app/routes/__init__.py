from fastapi import APIRouter

from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .websites import router as websites_router
from .node import router as node_router
from .database import router as databases_router
from .docker import router as docker_router
from .firewall import router as firewall_router
from .files import router as files_router
from .samba import router as samba_router
from .cloudflared import router as cloudflared_router
from .terminal import router as terminal_router
from .settings import router as settings_router

master_router = APIRouter()

master_router.include_router(auth_router)
master_router.include_router(dashboard_router)
master_router.include_router(websites_router)
master_router.include_router(node_router)
master_router.include_router(databases_router)
master_router.include_router(docker_router)
master_router.include_router(firewall_router)
master_router.include_router(files_router)
master_router.include_router(samba_router)
master_router.include_router(cloudflared_router)
master_router.include_router(terminal_router)
master_router.include_router(settings_router)
