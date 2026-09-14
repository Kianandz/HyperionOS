from fastapi import Request, Form, Depends, responses
from app.core.security import verify_session
from app.services import docker as docker_svc
from . import router


@router.post("/action")
async def container_action(
    container_id: str = Form(...),
    action: str = Form(...),
    image_name: str = Form(None),
    _: str = Depends(verify_session),
):
    docker_svc.container_action(container_id, action, image_name)
    return responses.RedirectResponse(url="/docker", status_code=303)


@router.get("/api/container/{container_id}")
async def get_container_info(container_id: str, _: str = Depends(verify_session)):
    return docker_svc.get_container_details(container_id)


@router.post("/api/container/update")
async def update_container_config(request: Request, _: str = Depends(verify_session)):
    data = await request.json()
    result = docker_svc.update_container(data)

    if result["status"] == "success":
        return result
    return responses.JSONResponse(status_code=500, content=result)
