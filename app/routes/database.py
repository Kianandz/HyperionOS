from fastapi import APIRouter, Request, Form, Depends, responses
from fastapi.templating import Jinja2Templates
from app.core.security import verify_session
from app.services import database_service
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/databases", tags=["Databases"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def databases_page(request: Request, user: str = Depends(verify_session)):
    mysql_installed = database_service.check_mysql_installed()
    return templates.TemplateResponse(
        request=request,
        name="pages/databases.html",
        context={"user": user, "active_page": "databases", "mysql_installed": mysql_installed}
    )

@router.post("/install-local", response_class=responses.HTMLResponse)
async def install_mysql(user: str = Depends(verify_session)):
    res = database_service.install_local_mysql()
    color = "emerald" if res["status"] == "success" else "red"
    return f'<div class="p-3 bg-{color}-500/10 border border-{color}-500/20 text-{color}-400 rounded-lg text-xs">{res["message"]}</div>'

@router.post("/query", response_class=responses.HTMLResponse)
async def execute_custom_query(
    request: Request,
    db_type: str = Form("mysql"),
    host: str = Form("127.0.0.1"),
    port: int = Form(3306),
    user_db: str = Form(..., alias="user"),
    password: str = Form(""),
    database: str = Form(""),
    query: str = Form(...)
):
    # Logika eksekusi SQL ke database service
    res = database_service.execute_raw_sql(db_type, host, port, user_db, password, database, query)
    return templates.TemplateResponse(
        request=request,
        name="components/databases/db_query_result.html",
        context={"result": res, "query": query}
    )

@router.post("/tables", response_class=responses.HTMLResponse)
async def fetch_tables(
    request: Request,
    db_type: str = Form("mysql"),
    host: str = Form("127.0.0.1"),
    port: int = Form(3306),
    user_db: str = Form("root", alias="user"), # Ubah dari Form(...) agar punya fallback
    password: str = Form(""),
    database: str = Form("") # Ubah dari Form(...) menjadi Form("") agar tidak 422 saat string kosong
):
    # Cegah eksekusi ke database service jika user memilih opsi "-- Pilih Database --"
    if not database:
        return '<div class="p-3 text-slate-500 text-xs italic">Pilih database terlebih dahulu...</div>'
        
    res = database_service.get_database_structure(db_type, host, port, user_db, password, database)
    return templates.TemplateResponse(
        request=request,
        name="components/databases/db_tables_sidebar.html",
        context={"result": res, "database": database}
    )

@router.post("/batch-action", response_class=responses.HTMLResponse)
async def batch_action(
    action: str = Form(...), table: str = Form(...), primary_key: str = Form("id"),
    row_ids: list[str] = Form([]), db_type: str = Form("mysql"),
    host: str = Form(...), port: int = Form(...), user_db: str = Form(..., alias="user"),
    password: str = Form(...), database: str = Form(...)
):
    if not row_ids:
        return '<div class="text-amber-400 text-xs p-2">Pilih minimal satu baris data!</div>'
    
    res = database_service.execute_batch_action(db_type, host, port, user_db, password, database, table, action, primary_key, row_ids)
    return f'<div class="text-emerald-400 text-xs p-2">Berhasil {action} {res["affected_rows"]} baris.</div>'

@router.post("/list-dbs", response_class=responses.HTMLResponse)
async def list_databases(
    request: Request,
    db_type: str = Form("mysql"), host: str = Form("127.0.0.1"), port: int = Form(3306),
    user_db: str = Form(..., alias="user"), password: str = Form("")
):
    res = database_service.get_all_databases(db_type, host, port, user_db, password)
    return templates.TemplateResponse(
        request=request,
        name="components/databases/db_selector.html",
        context={
            "result": res, "db_type": db_type, "host": host,
            "port": port, "user": user_db, "password": password
        }
    )

@router.post("/update-row", response_class=responses.HTMLResponse)
async def update_row_data(
    request: Request, table: str = Form(...), primary_key: str = Form("id"), pk_value: str = Form(...),
    db_type: str = Form(...), host: str = Form(...), port: int = Form(...),
    user_db: str = Form(..., alias="user"), password: str = Form(...), database: str = Form(...)
):
    form_data = dict(await request.form())
    
    # Buang key bawaan dari form buat nyisain data kolom murni yang mau diupdate
    exclude_keys = {"table", "primary_key", "pk_value", "db_type", "host", "port", "user", "password", "database"}
    update_data = {k: v for k, v in form_data.items() if k not in exclude_keys}
            
    res = database_service.update_row(db_type, host, port, user_db, password, database, table, primary_key, pk_value, update_data)
    
    if res.get("status") == "error":
        return f'<div class="text-rose-400 text-xs p-2">Error: {res["message"]}</div>'
    return f'<div class="text-emerald-400 text-xs p-2">Berhasil update {res["affected_rows"]} baris! (Jalankan ulang query buat refresh)</div>'

@router.post("/structure", response_class=responses.HTMLResponse)
async def fetch_structure(
    request: Request, db_type: str = Form("mysql"), host: str = Form(...), port: int = Form(...),
    user_db: str = Form(..., alias="user"), password: str = Form(""), database: str = Form(...), table: str = Form(...)
):
    res = database_service.get_table_structure(db_type, host, port, user_db, password, database, table)
    # Tambahkan context "table" biar UI tau ini lagi buka struktur tabel apa
    return templates.TemplateResponse(
        request, 
        name="components/databases/db_query_result.html", 
        context={"result": res, "query": f"SHOW FULL COLUMNS FROM `{table}`", "table": table}
    )

@router.post("/create-db")
async def api_create_db(
    db_name: str = Form(...), db_type: str = Form("mysql"), host: str = Form(...),
    port: int = Form(...), user_db: str = Form(..., alias="user"), password: str = Form("")
):
    res = database_service.create_database(db_type, host, port, user_db, password, db_name)
    return JSONResponse(res)

@router.post("/create-table")
async def api_create_table(
    table_name: str = Form(...), columns: str = Form(...), database: str = Form(...), 
    db_type: str = Form("mysql"), host: str = Form(...), port: int = Form(...), 
    user_db: str = Form(..., alias="user"), password: str = Form("")
):
    res = database_service.create_table(db_type, host, port, user_db, password, database, table_name, columns)
    return JSONResponse(res)

@router.post("/add-column")
async def api_add_column(
    table: str = Form(...), column_data: str = Form(...), database: str = Form(...), 
    db_type: str = Form("mysql"), host: str = Form(...), port: int = Form(...), 
    user_db: str = Form(..., alias="user"), password: str = Form("")
):
    import json
    col_data = json.loads(column_data)
    res = database_service.add_table_column(db_type, host, port, user_db, password, database, table, col_data)
    return JSONResponse(res)

@router.post("/batch-structure-action", response_class=responses.HTMLResponse)
async def api_batch_structure_action(
    action: str = Form(...), table: str = Form(...),
    row_ids: list[str] = Form([]), db_type: str = Form("mysql"),
    host: str = Form(...), port: int = Form(...), user_db: str = Form(..., alias="user"),
    password: str = Form(""), database: str = Form(...)
):
    # Note: 'row_ids' di mode ini isinya adalah nama-nama kolom/field
    if not row_ids:
        return '<div class="text-amber-400 text-xs p-2">Pilih minimal satu kolom!</div>'
    
    res = database_service.execute_batch_structure_action(db_type, host, port, user_db, password, database, table, action, row_ids)
    
    if res.get("status") == "error":
        return f'<div class="text-rose-400 text-xs p-2">Error: {res["message"]}</div>'
        
    return f'<div class="text-emerald-400 text-xs p-2">Berhasil {action} {res["affected_columns"]} kolom.</div>'

@router.post("/drop-table")
async def api_drop_table(
    table: str = Form(...), database: str = Form(...), 
    db_type: str = Form("mysql"), host: str = Form(...), port: int = Form(...), 
    user_db: str = Form(..., alias="user"), password: str = Form("")
):
    res = database_service.drop_table(db_type, host, port, user_db, password, database, table)
    return JSONResponse(res)

@router.post("/insert-row", response_class=responses.HTMLResponse)
async def api_insert_row(
    request: Request, table: str = Form(...),
    db_type: str = Form(...), host: str = Form(...), port: int = Form(...),
    user_db: str = Form(..., alias="user"), password: str = Form(...), database: str = Form(...)
):
    form_data = dict(await request.form())
    
    # Buang key kredensial server biar sisa data murni kolom aja
    exclude_keys = {"table", "db_type", "host", "port", "user", "password", "database"}
    # Filter field yang kosong (misal ID auto increment sengaja dikosongin dari UI)
    insert_data = {k: v for k, v in form_data.items() if k not in exclude_keys and v != ""}
            
    res = database_service.insert_row(db_type, host, port, user_db, password, database, table, insert_data)
    
    if res.get("status") == "error":
        return f'<div class="text-rose-400 text-xs p-2">Error: {res["message"]}</div>'
    return f'<div class="text-emerald-400 text-xs p-2">Berhasil menambahkan {res["affected_rows"]} baris! (Query otomatis di-refresh)</div>'