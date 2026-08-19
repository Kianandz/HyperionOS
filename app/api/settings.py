from fastapi import APIRouter
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

@router.get("/info")
def get_settings():

    return {
        "app_name": os.getenv("TITLE"),

        "version": os.getenv("VERSION"),

        "author": os.getenv("DEV"),

        "environment": "Arch Linux"
        
    }