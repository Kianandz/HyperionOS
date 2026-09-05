import os
import shutil
import pydantic
from fastapi import APIRouter, Request, Form, Depends, responses
from fastapi.templating import Jinja2Templates
from fastapi import File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from app.core.security import verify_session
from app.services import website_service

router = APIRouter(prefix="/websites", tags=["Websites"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def websites_page(request: Request, user: str = Depends(verify_session)):
    sites = website_service.list_websites()
    status_nginx = website_service.get_service_status("nginx")
    status_php = website_service.get_service_status("php-fpm")
    
    return templates.TemplateResponse(
        request=request,
        name="pages/websites.html",
        context={
            "user": user,
            "sites": sites,
            "nginx": status_nginx,
            "php_fpm": status_php,
            "active_page": "websites"
        }
    )

import os
# Pastiin module os udah di-import di atas

@router.post("/save")
async def save_site(
    domain: str = Form(...),
    mode: str = Form("simple"),
    site_type: str = Form("proxy"),
    port: int = Form(8000),
    root_dir: str = Form("/var/www/html"),
    raw_config: str = Form(""),
    _ : str = Depends(verify_session)
):
    # Otomatis bikin folder root_dir kalau belum ada
    if root_dir.startswith("/var/www/html/"):
        os.makedirs(root_dir, exist_ok=True)
        
        # Bikin file index default biar gak kosong melompong
        index_file = os.path.join(root_dir, "index.php" if site_type == "php" else "index.html")
        if not os.path.exists(index_file):
            with open(index_file, "w") as f:
                if site_type == "php":
                    f.write(f"<?php\necho '<h1>Welcome to {domain}</h1>';\necho '<p>PHP is working! Created via HyperionOS.</p>';\n?>")
                else:
                    f.write(f"<h1>Welcome to {domain}</h1>\n<p>Static/Proxy page created via HyperionOS.</p>")

    # Lanjut save config nginx
    website_service.save_website(domain=domain, mode=mode, site_type=site_type, port=port, root_dir=root_dir, raw_config=raw_config)
    return responses.RedirectResponse(url="/websites", status_code=303)

@router.post("/toggle/{domain}")
async def toggle_site(domain: str, _ : str = Depends(verify_session)):
    website_service.toggle_website(domain)
    return responses.RedirectResponse(url="/websites", status_code=303)

@router.post("/delete/{domain}")
async def delete_site(domain: str, _ : str = Depends(verify_session)):
    website_service.delete_website(domain)
    return responses.RedirectResponse(url="/websites", status_code=303)

@router.post("/control/{service}/{action}")
async def control_service(service: str, action: str, _ : str = Depends(verify_session)):
    if service == "nginx":
        website_service.control_nginx(action)
    elif service == "php":
        website_service.control_php_fpm(action)
    return responses.RedirectResponse(url="/websites", status_code=303)

@router.get("/config/{domain}")
async def get_config(domain: str, _ : str = Depends(verify_session)):
    raw_conf = website_service.get_website_config(domain)
    return {"domain": domain, "config": raw_conf}

@router.get("/logs/{service}")
async def get_logs(service: str, _ : str = Depends(verify_session)):
    # service isinya bisa "nginx" atau "php"
    logs = website_service.get_service_logs(service)
    return responses.PlainTextResponse(logs)

@router.get("/files/list/{domain}")
async def list_files(domain: str, subpath: str = "", _ : str = Depends(verify_session)):
    base_dir = f"/var/www/html/{domain}"
    target_dir = os.path.normpath(os.path.join(base_dir, subpath))
    
    # Kunci mampus biar gak bisa keluar dari base_dir
    if not target_dir.startswith(base_dir): target_dir = base_dir
    if not os.path.exists(target_dir): return JSONResponse({"files": []})
    
    files_data = []
    for f in os.listdir(target_dir):
        full = os.path.join(target_dir, f)
        files_data.append({"name": f, "is_dir": os.path.isdir(full), "size": os.path.getsize(full) if not os.path.isdir(full) else 0})
    return JSONResponse({"files": sorted(files_data, key=lambda x: x["is_dir"], reverse=True)})

@router.post("/files/upload/{domain}")
async def upload_files(domain: str, files: list[UploadFile] = File(...), subpath: str = Form(""), _ : str = Depends(verify_session)):
    base_dir = os.path.normpath(os.path.join(f"/var/www/html/{domain}", subpath))
    if not base_dir.startswith(f"/var/www/html/{domain}"): return JSONResponse({"error": "Unauthorized"}, status_code=403)
    os.makedirs(base_dir, exist_ok=True)
    
    for file in files:
        safe_path = os.path.join(base_dir, file.filename)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    return JSONResponse({"status": "success"})

@router.get("/files/download/{domain}/{filename:path}")
async def download_file(domain: str, filename: str, _ : str = Depends(verify_session)):
    file_path = f"/var/www/html/{domain}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename.split('/')[-1])
    return JSONResponse({"error": "File not found"}, status_code=404)

@router.post("/files/delete/{domain}/{filename:path}")
async def delete_file(domain: str, filename: str, _ : str = Depends(verify_session)):
    file_path = f"/var/www/html/{domain}/{filename}"
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    return JSONResponse({"status": "success"})

@router.post("/files/create/{domain}")
async def create_item(domain: str, name: str = Form(...), type: str = Form(...), subpath: str = Form(""), _ : str = Depends(verify_session)):
    base_dir = os.path.normpath(os.path.join(f"/var/www/html/{domain}", subpath))
    if not base_dir.startswith(f"/var/www/html/{domain}"): return JSONResponse({"error": "Unauthorized"}, status_code=403)
    path = os.path.join(base_dir, name)
    
    os.makedirs(path, exist_ok=True) if type == "folder" else open(path, 'a').close()
    return JSONResponse({"status": "success"})

@router.post("/files/action/{domain}")
async def file_actions(domain: str, action: str = Form(...), target: str = Form(...), dest: str = Form(""), mods: str = Form(""), _ : str = Depends(verify_session)):
    base_dir = f"/var/www/html/{domain}"
    src_path = os.path.normpath(os.path.join(base_dir, target))
    dest_path = os.path.normpath(os.path.join(base_dir, dest)) if dest else ""
    
    if not src_path.startswith(base_dir) or (dest and not dest_path.startswith(base_dir)):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    if action == "copy": shutil.copytree(src_path, dest_path) if os.path.isdir(src_path) else shutil.copy2(src_path, dest_path)
    elif action == "move": shutil.move(src_path, dest_path)
    elif action == "chmod": os.chmod(src_path, int(mods, 8))
    return JSONResponse({"status": "success"})

@router.get("/files/read/{domain}/{filename:path}")
async def read_file_content(domain: str, filename: str, _ : str = Depends(verify_session)):
    with open(f"/var/www/html/{domain}/{filename}", 'r') as f:
        return JSONResponse({"content": f.read()})

@router.post("/files/write/{domain}/{filename:path}")
async def write_file_content(domain: str, filename: str, content: str = Form(...), _ : str = Depends(verify_session)):
    with open(f"/var/www/html/{domain}/{filename}", 'w') as f:
        f.write(content)
    return JSONResponse({"status": "success"})

@router.get("/config/{domain}")
async def get_config(domain: str, _ : str = Depends(verify_session)):
    try:
        raw_conf = website_service.get_website_config(domain)
        return JSONResponse({"status": "success", "config": raw_conf})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=404)