from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.docker_service import get_docker_overview, list_containers, container_action, get_container_details, install_and_run

class InstallSchema(BaseModel):
    image_name: str

router = APIRouter()

class ActionSchema(BaseModel):

    container_id: str

    action: str

@router.get("/overview")
def overview():

    return get_docker_overview()

@router.get("/containers")
def containers():

    return list_containers()

@router.post("/action")
def do_action(data: ActionSchema):

    res = container_action(data.container_id, data.action)

    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    
    return res

@router.get("/container/{container_id}")
def container_details(container_id: str):

    return get_container_details(container_id)

@router.post("/install")
def install_app(data: InstallSchema):

    res = install_and_run(data.image_name)
    
    if res["status"] == "error":

        raise HTTPException(status_code=400, detail=res["message"])
    
    return res