from fastapi import APIRouter, Request, Form, Depends, responses, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from app.core.security import verify_session
from app.services import files_service
import shutil
import os
import tempfile
import json
from flask import request, redirect, flash
from typing import List

router = APIRouter(prefix="/files", tags=["Files"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def files_page(request: Request, path: str = "", user: str = Depends(verify_session)):
    contents = files_service.get_directory_contents(path)
    return templates.TemplateResponse(
        request=request, 
        name="pages/files.html", 
        context={
            "user": user,
            "contents": contents,
            "active_page": "files"
        }
    )

@router.get("/download")
async def download_item(path: str, _ : str = Depends(verify_session)):
    target_path = files_service.get_safe_path(path)
    if os.path.isdir(target_path):
        tmp_dir = tempfile.gettempdir()
        zip_filename = os.path.basename(target_path) or "archive"
        zip_path = os.path.join(tmp_dir, zip_filename)
        shutil.make_archive(zip_path, 'zip', target_path)
        return FileResponse(f"{zip_path}.zip", media_type="application/zip", filename=f"{zip_filename}.zip")
    return FileResponse(target_path)

@router.post("/upload")
async def upload_file(path: str = Form(""), file: List[UploadFile] = File(...), _ : str = Depends(verify_session)):
    target_dir = files_service.get_safe_path(path)

    for f in file:
        # Mengamankan struktur subfolder kalau upload via webkitdirectory
        dest_path = os.path.join(target_dir, f.filename)

        # Bikin otomatis foldernya kalau belum ada di storage
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(dest_path, "wb+") as dest_f:
            shutil.copyfileobj(f.file, dest_f)

    return responses.RedirectResponse(url=f"/files?path={path}", status_code=303)

@router.post("/delete")
async def delete_item(path: str = Form(...), _ : str = Depends(verify_session)):
    files_service.delete_path(path)
    parent_dir = os.path.dirname(path)
    return responses.RedirectResponse(url=f"/files?path={parent_dir}", status_code=303)

@router.post("/batch-delete")
async def batch_delete_items(paths_json: str = Form(...), current_path: str = Form(""), _ : str = Depends(verify_session)):
    paths = json.loads(paths_json)
    files_service.delete_batch(paths)
    return responses.RedirectResponse(url=f"/files?path={current_path}", status_code=303)

@router.post("/create-folder")
async def create_new_folder(path: str = Form(""), folder_name: str = Form(...), _ : str = Depends(verify_session)):
    files_service.create_folder(path, folder_name)
    return responses.RedirectResponse(url=f"/files?path={path}", status_code=303)

@router.post("/create-file")
async def create_new_file(path: str = Form(""), file_name: str = Form(...), _ : str = Depends(verify_session)):
    files_service.create_file(path, file_name)
    return responses.RedirectResponse(url=f"/files?path={path}", status_code=303)

@router.post("/rename")
async def rename_file_folder(path: str = Form(...), new_name: str = Form(...), _ : str = Depends(verify_session)):
    files_service.rename_item(path, new_name)
    parent_dir = os.path.dirname(path)
    return responses.RedirectResponse(url=f"/files?path={parent_dir}", status_code=303)

@router.post("/transfer")
async def transfer_file_folder(src_path: str = Form(...), dest_dir: str = Form(...), action: str = Form(...), _ : str = Depends(verify_session)):
    files_service.transfer_item(src_path, dest_dir, action)
    return responses.RedirectResponse(url=f"/files?path={dest_dir}", status_code=303)

@router.post("/batch-transfer")
async def batch_transfer(
    paths_json: str = Form("[]"), 
    action: str = Form(...), 
    dest_dir: str = Form(""), 
    _ : str = Depends(verify_session)
):
    try:
        paths = json.loads(paths_json)
        # Proteksi 1: Pastikan paths selalu berbentuk list
        if isinstance(paths, str):
            paths = [paths]
    except Exception:
        return responses.RedirectResponse(url=f"/files?path={dest_dir}", status_code=303)

    # FIX: Ambil path yang benar pakai files_service bawaan lu
    target_dest_path = files_service.get_safe_path(dest_dir)

    for p in paths:
        p = str(p).strip()
        
        # Proteksi 2: Tolak mentah-mentah jika path kosong, titik (.), atau root
        if not p or p == '.' or p == '/':
            continue

        # FIX: Ambil source path yang bener
        src_path = files_service.get_safe_path(p)

        # Proteksi 3: Mencegah infinite recursive loop (blackhole)
        if target_dest_path.startswith(src_path):
            print(f"Bahaya Rekursif: {src_path} dicegah agar tidak masuk ke {target_dest_path}")
            continue

        # Eksekusi Copy/Move
        if os.path.exists(src_path):
            dest_file_path = os.path.join(target_dest_path, os.path.basename(src_path))
            
            try:
                if action == 'copy':
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dest_file_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dest_file_path)
                elif action == 'move':
                    shutil.move(src_path, dest_file_path)
            except Exception as e:
                print(f"Gagal transfer {src_path}: {e}")
                pass 

    return responses.RedirectResponse(url=f"/files?path={dest_dir}", status_code=303)

@router.post("/extract")
async def extract_zip(path: str = Form(...), _ : str = Depends(verify_session)):
    files_service.extract_archive(path)
    parent_dir = os.path.dirname(path)
    return responses.RedirectResponse(url=f"/files?path={parent_dir}", status_code=303)

@router.post("/compress")
async def compress_zip(path: str = Form(...), _ : str = Depends(verify_session)):
    full_path = files_service.get_safe_path(path)
    parent_dir = os.path.dirname(path)
    base_name = os.path.basename(full_path) + ".zip"
    files_service.compress_items([path], parent_dir, base_name)
    return responses.RedirectResponse(url=f"/files?path={parent_dir}", status_code=303)

@router.post("/batch-compress")
async def batch_compress_items(paths_json: str = Form(...), current_path: str = Form(""), zip_name: str = Form("archive.zip"), _ : str = Depends(verify_session)):
    paths = json.loads(paths_json)
    files_service.compress_items(paths, current_path, zip_name)
    return responses.RedirectResponse(url=f"/files?path={current_path}", status_code=303)

# API FOR TEXT EDITOR
@router.get("/api/read-file")
async def api_read_file(path: str, _ : str = Depends(verify_session)):
    return JSONResponse(content=files_service.read_file(path))

@router.post("/api/write-file")
async def api_write_file(path: str = Form(...), content: str = Form(...), _ : str = Depends(verify_session)):
    return JSONResponse(content=files_service.write_file(path, content))