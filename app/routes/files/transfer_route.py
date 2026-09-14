import os, tempfile, shutil, json
from fastapi import Form, UploadFile, File, Depends, responses
from fastapi.responses import FileResponse
from app.core.security import verify_session
from app.services import files as fm_svc
from . import router
from typing import List


@router.get("/download")
async def download_item(path: str, _: str = Depends(verify_session)):
    target_path = fm_svc.get_safe_path(path)
    if os.path.isdir(target_path):
        zip_path = os.path.join(
            tempfile.gettempdir(), os.path.basename(target_path) or "archive"
        )
        shutil.make_archive(zip_path, "zip", target_path)
        return FileResponse(
            f"{zip_path}.zip",
            media_type="application/zip",
            filename=f"{os.path.basename(target_path)}.zip",
        )
    return FileResponse(target_path)


@router.post("/upload")
async def upload_file(
    path: str = Form(""),
    file: List[UploadFile] = File(...),
    _: str = Depends(verify_session),
):
    target_dir = fm_svc.get_safe_path(path)
    for f in file:
        dest_path = os.path.join(target_dir, f.filename)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb+") as dest_f:
            shutil.copyfileobj(f.file, dest_f)
    return responses.RedirectResponse(url=f"/files?path={path}", status_code=303)


@router.post("/transfer")
async def transfer_file_folder(
    src_path: str = Form(...),
    dest_dir: str = Form(...),
    action: str = Form(...),
    _: str = Depends(verify_session),
):
    fm_svc.transfer_item(src_path, dest_dir, action)
    return responses.RedirectResponse(url=f"/files?path={dest_dir}", status_code=303)


@router.post("/batch-transfer")
async def batch_transfer(
    paths_json: str = Form("[]"),
    action: str = Form(...),
    dest_dir: str = Form(""),
    _: str = Depends(verify_session),
):
    try:
        paths = json.loads(paths_json)
        if isinstance(paths, str):
            paths = [paths]
    except Exception:
        return responses.RedirectResponse(
            url=f"/files?path={dest_dir}", status_code=303
        )

    target_dest_path = fm_svc.get_safe_path(dest_dir)
    for p in paths:
        p = str(p).strip()
        if not p or p in [".", "/"]:
            continue
        src_path = fm_svc.get_safe_path(p)
        if target_dest_path.startswith(src_path) or not os.path.exists(src_path):
            continue

        dest_file_path = os.path.join(target_dest_path, os.path.basename(src_path))
        try:
            if action == "copy":
                (
                    shutil.copytree(src_path, dest_file_path, dirs_exist_ok=True)
                    if os.path.isdir(src_path)
                    else shutil.copy2(src_path, dest_file_path)
                )
            elif action == "move":
                shutil.move(src_path, dest_file_path)
        except Exception:
            pass
    return responses.RedirectResponse(url=f"/files?path={dest_dir}", status_code=303)
