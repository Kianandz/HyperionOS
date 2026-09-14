from fastapi import Form, Depends
from app.core.security import verify_session
from app.services import docker as docker_svc
from . import router


@router.post("/api/terminal")
async def run_terminal(
    container_id: str = Form(...),
    command: str = Form(...),
    _: str = Depends(verify_session),
):
    return docker_svc.run_container_command(container_id, command)


@router.get("/api/logs/{container_id}")
async def get_container_logs_api(container_id: str, _: str = Depends(verify_session)):
    return docker_svc.get_container_logs(container_id)
