from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.files_service import get_directory_contents, delete_path

router = APIRouter()

class FileDeleteSchema(BaseModel):

    path: str

@router.get("/list")
def list_files(path: str = ""):

    res = get_directory_contents(path)

    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    
    return res

@router.post("/delete")
def remove_file(data: FileDeleteSchema):

    res = delete_path(data.path)

    if res["status"] == "error":
        raise HTTPException(status_code=400, detail=res["message"])
    
    return res