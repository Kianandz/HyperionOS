from fastapi import Request, Form, responses
from fastapi.responses import JSONResponse
from app.services import database as db_svc
from . import router, templates


@router.post("/list-dbs", response_class=responses.HTMLResponse)
async def list_databases(
    request: Request,
    db_type: str = Form("mysql"),
    host: str = Form("127.0.0.1"),
    port: int = Form(3306),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
):
    res = db_svc.get_all_databases(db_type, host, port, user_db, password)
    return templates.TemplateResponse(
        request=request,
        name="components/databases/db_selector.html",
        context={
            "result": res,
            "db_type": db_type,
            "host": host,
            "port": port,
            "user": user_db,
            "password": password,
        },
    )


@router.post("/create-db")
async def api_create_db(
    db_name: str = Form(...),
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
):
    res = db_svc.create_database(db_type, host, port, user_db, password, db_name)
    return JSONResponse(res)
