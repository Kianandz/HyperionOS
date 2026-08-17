from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.website_service import (
    list_websites, get_website_config, save_website, toggle_website, delete_website,

    get_service_status, control_nginx,
    
    control_php_fpm, get_service_logs, read_php_config, save_php_config

)

router = APIRouter()

class WebsiteSaveSchema(BaseModel):

    domain: str

    mode: str = "simple"

    site_type: str = "proxy"

    port: Optional[int] = 8000

    root_dir: Optional[str] = "/var/www/html"

    php_sock: Optional[str] = "/run/php-fpm/php-fpm.sock"

    max_body_size: Optional[str] = "64M"

    raw_config: Optional[str] = ""

class PhpConfigPayload(BaseModel):

    config: str

@router.get("/")
def get_all_sites():

    return {"sites": list_websites()}

@router.get("/status")
def get_status():

    return {

        "nginx": get_service_status("nginx"),

        "php_fpm": get_service_status("php-fpm")

    }

@router.post("/nginx/{action}")
def nginx_action(action: str):

    try:

        return control_nginx(action)
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@router.post("/php-fpm/{action}")
def php_fpm_action(action: str):

    try:

        return control_php_fpm(action)
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/logs/{target}")
def get_logs(target: str):

    try:

        return {"logs": get_service_logs(target)}
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/php-config")
def get_php_config():

    try:

        return read_php_config()
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@router.post("/php-config")
def update_php_config(payload: PhpConfigPayload):

    try:

        return save_php_config(payload.config)
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/config/{domain}")
def get_config(domain: str):

    try:

        return {"config": get_website_config(domain)}
    
    except Exception as e:

        raise HTTPException(status_code=404, detail=str(e))
    

@router.post("/save")
def save_site(data: WebsiteSaveSchema):

    try:

        res = save_website(

            domain=data.domain, mode=data.mode, site_type=data.site_type,

            port=data.port, root_dir=data.root_dir, php_sock=data.php_sock,

            max_body_size=data.max_body_size, raw_config=data.raw_config

        )

        return res
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/toggle/{domain}")
def toggle_site(domain: str):

    try:

        return toggle_website(domain)
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/{domain}")
def remove_site(domain: str):

    try:

        return delete_website(domain)
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))
    