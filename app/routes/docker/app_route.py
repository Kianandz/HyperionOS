from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import docker as docker_svc
from . import router


@router.post("/api/install")
async def api_install_app(
    image: str = Form(...),
    title: str = Form(...),
    default_port: int = Form(80),
    container_port: int = Form(80),
    _: str = Depends(verify_session),
):
    container_name = title.lower().replace(" ", "-")
    host_port = docker_svc.get_available_port(default_port)

    data = {
        "image_name": image,
        "name": container_name,
        "ports": {f"{container_port}/tcp": host_port},
        "env": ["TZ=Asia/Jakarta"],
        "volumes": [],
        "mem_limit": "512m",
        "cpu_shares": 512,
    }

    result = docker_svc.install_and_run(data)

    if result["status"] == "success":
        return {"status": "success", "message": result["message"], "port": host_port}
    return responses.JSONResponse(status_code=500, content=result)
