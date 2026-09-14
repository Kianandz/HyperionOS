from fastapi import Request, Depends, responses
from app.core.security import verify_session
from app.services import docker as docker_svc
from . import router, templates


@router.get("", response_class=responses.HTMLResponse)
async def docker_page(request: Request, user: str = Depends(verify_session)):
    overview = docker_svc.get_docker_overview()
    containers = docker_svc.list_containers()
    images = docker_svc.get_images()

    return templates.TemplateResponse(
        request=request,
        name="pages/docker.html",
        context={
            "user": user,
            "overview": overview,
            "containers": containers,
            "images": images,
            "active_page": "docker",
        },
    )
