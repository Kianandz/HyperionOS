import json
from fastapi import Request, Form, responses
from fastapi.responses import JSONResponse
from app.services import database as db_svc
from . import router, templates


@router.post("/tables", response_class=responses.HTMLResponse)
async def fetch_tables(
    request: Request,
    db_type: str = Form("mysql"),
    host: str = Form("127.0.0.1"),
    port: int = Form(3306),
    user_db: str = Form("root", alias="user"),
    password: str = Form(""),
    database: str = Form(""),
):
    if not database:
        return '<div class="p-3 text-slate-500 text-xs italic">Choose database first!</div>'

    res = db_svc.get_database_structure(
        db_type, host, port, user_db, password, database
    )
    return templates.TemplateResponse(
        request=request,
        name="components/databases/db_tables_sidebar.html",
        context={"result": res, "database": database},
    )


@router.post("/structure", response_class=responses.HTMLResponse)
async def fetch_structure(
    request: Request,
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
    database: str = Form(...),
    table: str = Form(...),
):
    res = db_svc.get_table_structure(
        db_type, host, port, user_db, password, database, table
    )
    return templates.TemplateResponse(
        request,
        name="components/databases/db_query_result.html",
        context={
            "result": res,
            "query": f"SHOW FULL COLUMNS FROM `{table}`",
            "table": table,
        },
    )


@router.post("/create-table")
async def api_create_table(
    table_name: str = Form(...),
    columns: str = Form(...),
    database: str = Form(...),
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
):
    res = db_svc.create_table(
        db_type, host, port, user_db, password, database, table_name, columns
    )
    return JSONResponse(res)


@router.post("/add-column")
async def api_add_column(
    table: str = Form(...),
    column_data: str = Form(...),
    database: str = Form(...),
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
):
    col_data = json.loads(column_data)
    res = db_svc.add_table_column(
        db_type, host, port, user_db, password, database, table, col_data
    )
    return JSONResponse(res)


@router.post("/batch-structure-action", response_class=responses.HTMLResponse)
async def api_batch_structure_action(
    action: str = Form(...),
    table: str = Form(...),
    row_ids: list[str] = Form([]),
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
    database: str = Form(...),
):
    if not row_ids:
        return '<div class="text-amber-400 text-xs p-2">Choose fields first!</div>'
    res = db_svc.execute_batch_structure_action(
        db_type, host, port, user_db, password, database, table, action, row_ids
    )
    if res.get("status") == "error":
        return f'<div class="text-rose-400 text-xs p-2">Error: {res["message"]}</div>'
    return f'<div class="text-emerald-400 text-xs p-2">Success {action} {res["affected_columns"]} row.</div>'


@router.post("/drop-table")
async def api_drop_table(
    table: str = Form(...),
    database: str = Form(...),
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
):
    res = db_svc.drop_table(db_type, host, port, user_db, password, database, table)
    return JSONResponse(res)
