from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
def get_settings():

    return {
        "app_name": "HyperionOS",

        "version": "1.0.0",

        "author": "Kianandz",

        "environment": "Arch Linux"
        
    }