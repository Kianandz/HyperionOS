from fastapi import APIRouter, Request, Form, Depends, responses
from fastapi.templating import Jinja2Templates
from app.core.security import verify_session
from app.services import docker_service

router = APIRouter(prefix="/docker", tags=["Docker"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=responses.HTMLResponse)
async def docker_page(request: Request, user: str = Depends(verify_session)):
    overview = docker_service.get_docker_overview()
    containers = docker_service.list_containers()
    images = docker_service.get_images()
    
    return templates.TemplateResponse(
        request=request, 
        name="pages/docker.html", 
        context={
        "user": user,
        "overview": overview,
        "containers": containers,
        "images": images,
        "active_page": "docker"
    })

@router.post("/action")
async def container_action(
    container_id: str = Form(...), 
    action: str = Form(...),
    image_name: str = Form(None), # Tambahin ini buat nangkep image_name
    _ : str = Depends(verify_session)
):
    # Pass 3 parameter sekarang
    docker_service.container_action(container_id, action, image_name)
    return responses.RedirectResponse(url="/docker", status_code=303)

@router.post("/compose/deploy")
async def deploy_compose(
    project_name: str = Form(...),
    yaml_data: str = Form(...),
    _ : str = Depends(verify_session)
):
    docker_service.deploy_compose(yaml_data, project_name)
    return responses.RedirectResponse(url="/docker", status_code=303)

@router.post("/api/install")
async def api_install_app(
    image: str = Form(...),
    title: str = Form(...),
    default_port: int = Form(80), # Tambahin input default port
    container_port: int = Form(80),
    _ : str = Depends(verify_session)
):
    container_name = title.lower().replace(" ", "-")
    
    # Logic cari port aman
    host_port = docker_service.get_available_port(default_port)
    
    # Auto setup data
    data = {
        "image_name": image,
        "name": container_name,
        "ports": {f"{container_port}/tcp": host_port},
        "env": ["TZ=Asia/Jakarta"], # Default env
        "volumes": [], # Bisa di set otomatis juga tergantung app-nya
        "mem_limit": "512m", # Auto memory limit
        "cpu_shares": 512
    }
    
    result = docker_service.install_and_run(data)
    
    if result["status"] == "success":
        return {"status": "success", "message": result["message"], "port": host_port}
    return responses.JSONResponse(status_code=500, content=result)

@router.get("/api/container/{container_id}")
async def get_container_info(container_id: str, _ : str = Depends(verify_session)):
    return docker_service.get_container_details(container_id)

@router.get("/api/export/{container_id}")
async def export_compose(container_id: str, _ : str = Depends(verify_session)):
    return docker_service.export_container_compose(container_id)

@router.post("/api/terminal")
async def run_terminal(
    container_id: str = Form(...),
    command: str = Form(...),
    _ : str = Depends(verify_session)
):
    return docker_service.run_container_command(container_id, command)

@router.get("/api/logs/{container_id}")
async def get_container_logs_api(container_id: str, _ : str = Depends(verify_session)):
    return docker_service.get_container_logs(container_id)

# Tambahin endpoint ini di dalem docker.py
@router.post("/api/container/update")
async def update_container_config(request: Request, _ : str = Depends(verify_session)):
    # Ambil JSON yang dikirim JS
    data = await request.json()
    
    # Lempar ke service buat dieksekusi
    result = docker_service.update_container(data)
    
    if result["status"] == "success":
        return result
    return responses.JSONResponse(status_code=500, content=result)