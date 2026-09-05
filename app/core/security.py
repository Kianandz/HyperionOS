from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

def verify_session(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired, silakan login kembali."
        )
    return user