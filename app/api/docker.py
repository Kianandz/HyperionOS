from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.docker_service import get_docker_overview, list_containers, container_action

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