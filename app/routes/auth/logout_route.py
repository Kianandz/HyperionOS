from fastapi import Request, responses, status

from . import router


@router.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return responses.RedirectResponse(
        url="/login", status_code=status.HTTP_303_SEE_OTHER
    )
