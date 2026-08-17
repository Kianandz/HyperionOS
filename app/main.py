from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.dashboard import router as dashboard_router
from app.api.websites import router as websites_router
from app.api.databases import router as databases_router
from app.api.docker import router as docker_router
from app.api.firewall import router as firewall_router
from app.api.files import router as files_router
from app.api.cloudflared import router as cloudflared_router
from app.api.settings import router as settings_router
from app.api.auth import router as auth_router


app = FastAPI(title="HyperionOS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(websites_router, prefix="/api/websites", tags=["Websites"])
app.include_router(databases_router, prefix="/api/databases", tags=["Databases"])
app.include_router(docker_router, prefix="/api/docker", tags=["Docker"])
app.include_router(firewall_router, prefix="/api/firewall", tags=["Firewall"])
app.include_router(files_router, prefix="/api/files", tags=["Files"])
app.include_router(cloudflared_router, prefix="/api/cloudflared", tags=["Cloudflared"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])