import os, shutil, re
from fastapi import Form, File, UploadFile, Depends
from fastapi.responses import FileResponse, JSONResponse
from app.core.security import verify_session
from app.services import website
from . import router


def get_actual_root(domain: str) -> str:
    try:
        config = website.get_website_config(domain)
        match = re.search(r"root\s+([^;]+);", config)
        if match:
            return match.group(1).strip()
    except:
        pass
    return f"/var/www/html/{domain}"


@router.get("/files/list/{domain}")
async def list_files(domain: str, subpath: str = "", _: str = Depends(verify_session)):
    base_dir = get_actual_root(domain)
    target_dir = os.path.normpath(os.path.join(base_dir, subpath))

    if not target_dir.startswith(base_dir):
        target_dir = base_dir
    if not os.path.exists(target_dir):
        return JSONResponse({"files": [], "actual_root": base_dir})

    files_data = []
    for f in os.listdir(target_dir):
        full = os.path.join(target_dir, f)
        files_data.append(
            {
                "name": f,
                "is_dir": os.path.isdir(full),
                "size": os.path.getsize(full) if not os.path.isdir(full) else 0,
            }
        )
    return JSONResponse(
        {
            "files": sorted(files_data, key=lambda x: x["is_dir"], reverse=True),
            "actual_root": base_dir,
        }
    )


@router.post("/files/upload/{domain}")
async def upload_files(
    domain: str,
    files: list[UploadFile] = File(...),
    subpath: str = Form(""),
    _: str = Depends(verify_session),
):
    actual_root = get_actual_root(domain)
    base_dir = os.path.normpath(os.path.join(actual_root, subpath))

    if not base_dir.startswith(actual_root):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    os.makedirs(base_dir, exist_ok=True)

    for file in files:
        safe_path = os.path.join(base_dir, file.filename)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    return JSONResponse({"status": "success"})


@router.get("/files/download/{domain}/{filename:path}")
async def download_file(domain: str, filename: str, _: str = Depends(verify_session)):
    actual_root = get_actual_root(domain)
    file_path = os.path.normpath(os.path.join(actual_root, filename))

    if file_path.startswith(actual_root) and os.path.exists(file_path):
        return FileResponse(file_path, filename=filename.split("/")[-1])
    return JSONResponse({"error": "File not found"}, status_code=404)


@router.post("/files/delete/{domain}/{filename:path}")
async def delete_file(domain: str, filename: str, _: str = Depends(verify_session)):
    actual_root = get_actual_root(domain)
    file_path = os.path.normpath(os.path.join(actual_root, filename))

    if file_path.startswith(actual_root) and os.path.exists(file_path):
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    return JSONResponse({"status": "success"})


@router.post("/files/create/{domain}")
async def create_item(
    domain: str,
    name: str = Form(...),
    type: str = Form(...),
    subpath: str = Form(""),
    _: str = Depends(verify_session),
):
    actual_root = get_actual_root(domain)
    base_dir = os.path.normpath(os.path.join(actual_root, subpath))

    if not base_dir.startswith(actual_root):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    path = os.path.join(base_dir, name)

    os.makedirs(path, exist_ok=True) if type == "folder" else open(path, "a").close()
    return JSONResponse({"status": "success"})


@router.post("/files/action/{domain}")
async def file_actions(
    domain: str,
    action: str = Form(...),
    target: str = Form(...),
    dest: str = Form(""),
    mods: str = Form(""),
    _: str = Depends(verify_session),
):
    actual_root = get_actual_root(domain)
    src_path = os.path.normpath(os.path.join(actual_root, target))
    dest_path = os.path.normpath(os.path.join(actual_root, dest)) if dest else ""

    if not src_path.startswith(actual_root) or (
        dest and not dest_path.startswith(actual_root)
    ):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)

    if action == "copy":
        (
            shutil.copytree(src_path, dest_path)
            if os.path.isdir(src_path)
            else shutil.copy2(src_path, dest_path)
        )
    elif action == "move":
        shutil.move(src_path, dest_path)
    elif action == "chmod":
        os.chmod(src_path, int(mods, 8))
    return JSONResponse({"status": "success"})


@router.get("/files/read/{domain}/{filename:path}")
async def read_file_content(
    domain: str, filename: str, _: str = Depends(verify_session)
):
    actual_root = get_actual_root(domain)
    file_path = os.path.normpath(os.path.join(actual_root, filename))

    if not file_path.startswith(actual_root) or not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)

    with open(file_path, "r") as f:
        return JSONResponse({"content": f.read()})


@router.post("/files/write/{domain}/{filename:path}")
async def write_file_content(
    domain: str,
    filename: str,
    content: str = Form(...),
    _: str = Depends(verify_session),
):
    actual_root = get_actual_root(domain)
    file_path = os.path.normpath(os.path.join(actual_root, filename))

    if not file_path.startswith(actual_root):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)

    with open(file_path, "w") as f:
        f.write(content)
    return JSONResponse({"status": "success"})
