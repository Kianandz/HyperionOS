from fastapi import Request, Form, responses
from app.services import database as db_svc
from . import router, templates


@router.post("/query", response_class=responses.HTMLResponse)
async def execute_custom_query(
    request: Request,
    db_type: str = Form("mysql"),
    host: str = Form("127.0.0.1"),
    port: int = Form(3306),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
    database: str = Form(""),
    query: str = Form(...),
):
    res = db_svc.execute_raw_sql(
        db_type, host, port, user_db, password, database, query
    )
    return templates.TemplateResponse(
        request=request,
        name="components/databases/db_query_result.html",
        context={"result": res, "query": query},
    )
