from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import docker as docker_svc
from . import router


@router.post("/compose/deploy")
async def deploy_compose(
    project_name: str = Form(...),
    yaml_data: str = Form(...),
    _: str = Depends(verify_session),
):
    docker_svc.deploy_compose(yaml_data, project_name)
    return responses.RedirectResponse(url="/docker", status_code=303)


@router.get("/api/export/{container_id}")
async def export_compose(container_id: str, _: str = Depends(verify_session)):
    return docker_svc.export_container_compose(container_id)
