from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.database_service import test_db_connection, execute_custom_query

router = APIRouter()

class DBConnectSchema(BaseModel):

    db_type: str

    host: str

    port: int

    user: str

    password: str

    database: str = ""

class QueryExecuteSchema(BaseModel):

    db_type: str

    host: str

    port: int

    user: str

    password: str

    database: str

    query: str


@router.post("/test-connection")
def check_connection(data: DBConnectSchema):

    result = test_db_connection(
        data.db_type, data.host, data.port, data.user, data.password, data.database
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/query")
def run_query(data: QueryExecuteSchema):

    if not data.database:
        raise HTTPException(status_code=400, detail="Select database first!")
    
    result = execute_custom_query(
        data.db_type, data.host, data.port, data.user, 
        data.password, data.database, data.query
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result