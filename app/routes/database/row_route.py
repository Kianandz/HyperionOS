from fastapi import Request, Form, responses
from app.services import database as db_svc
from . import router


@router.post("/batch-action", response_class=responses.HTMLResponse)
async def batch_action(
    action: str = Form(...),
    table: str = Form(...),
    primary_key: str = Form("id"),
    row_ids: list[str] = Form([]),
    db_type: str = Form("mysql"),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(...),
    database: str = Form(...),
):
    if not row_ids:
        return '<div class="text-amber-400 text-xs p-2">Invalid action specified</div>'
    res = db_svc.execute_batch_action(
        db_type,
        host,
        port,
        user_db,
        password,
        database,
        table,
        action,
        primary_key,
        row_ids,
    )
    return f'<div class="text-emerald-400 text-xs p-2">Success {action} {res["affected_rows"]} row.</div>'


@router.post("/update-row", response_class=responses.HTMLResponse)
async def update_row_data(
    request: Request,
    table: str = Form(...),
    primary_key: str = Form("id"),
    pk_value: str = Form(...),
    db_type: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(...),
    database: str = Form(...),
):
    form_data = dict(await request.form())
    exclude_keys = {
        "table",
        "primary_key",
        "pk_value",
        "db_type",
        "host",
        "port",
        "user",
        "password",
        "database",
    }
    update_data = {k: v for k, v in form_data.items() if k not in exclude_keys}

    res = db_svc.update_row(
        db_type,
        host,
        port,
        user_db,
        password,
        database,
        table,
        primary_key,
        pk_value,
        update_data,
    )
    if res.get("status") == "error":
        return f'<div class="text-rose-400 text-xs p-2">Error: {res["message"]}</div>'
    return f'<div class="text-emerald-400 text-xs p-2">Update success on {res["affected_rows"]} row!</div>'


@router.post("/insert-row", response_class=responses.HTMLResponse)
async def api_insert_row(
    request: Request,
    table: str = Form(...),
    db_type: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    user_db: str = Form(..., alias="user"),
    password: str = Form(...),
    database: str = Form(...),
):
    form_data = dict(await request.form())
    exclude_keys = {"table", "db_type", "host", "port", "user", "password", "database"}
    insert_data = {
        k: v for k, v in form_data.items() if k not in exclude_keys and v != ""
    }

    res = db_svc.insert_row(
        db_type, host, port, user_db, password, database, table, insert_data
    )
    if res.get("status") == "error":
        return f'<div class="text-rose-400 text-xs p-2">Error: {res["message"]}</div>'
    return f'<div class="text-emerald-400 text-xs p-2">Add success on: {res["affected_rows"]} row!</div>'
