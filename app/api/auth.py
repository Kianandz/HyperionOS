from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.pam_service import verify_linux_user
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

class LoginSchema(BaseModel):

    username: str

    password: str

@router.post("/login")

def login(data: LoginSchema):

    if not verify_linux_user(data.username, data.password):

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED, 

            detail="Username or Password incorrect!"

        )
    
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=2)

    payload = {

        "sub": data.username,

        "exp": expire

    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {

        "message": "Login Success!", 

        "access_token": token,

        "token_type": "bearer",

        "user": data.username

    }