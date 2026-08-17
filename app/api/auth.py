from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.pam_service import verify_linux_user

router = APIRouter()

class LoginSchema(BaseModel):

    username: str

    password: str

@router.post("/login")
def login(data: LoginSchema):

    if not verify_linux_user(data.username, data.password):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Username atau password sistem salah"
        )

    return {"message": "Login berhasil", "user": data.username}