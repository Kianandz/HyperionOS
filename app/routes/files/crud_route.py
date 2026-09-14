import os, json
from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import files as fm_svc
from . import router


@router.post("/delete")
async def delete_item(path: str = Form(...), _: str = Depends(verify_session)):
    fm_svc.delete_path(path)
    return responses.RedirectResponse(
        url=f"/files?path={os.path.dirname(path)}", status_code=303
    )


@router.post("/batch-delete")
async def batch_delete_items(
    paths_json: str = Form(...),
    current_path: str = Form(""),
    _: str = Depends(verify_session),
):
    fm_svc.delete_batch(json.loads(paths_json))
    return responses.RedirectResponse(
        url=f"/files?path={current_path}", status_code=303
    )


@router.post("/create-folder")
async def create_new_folder(
    path: str = Form(""), folder_name: str = Form(...), _: str = Depends(verify_session)
):
    fm_svc.create_folder(path, folder_name)
    return responses.RedirectResponse(url=f"/files?path={path}", status_code=303)


@router.post("/create-file")
async def create_new_file(
    path: str = Form(""), file_name: str = Form(...), _: str = Depends(verify_session)
):
    fm_svc.create_file(path, file_name)
    return responses.RedirectResponse(url=f"/files?path={path}", status_code=303)


@router.post("/rename")
async def rename_file_folder(
    path: str = Form(...), new_name: str = Form(...), _: str = Depends(verify_session)
):
    fm_svc.rename_item(path, new_name)
    return responses.RedirectResponse(
        url=f"/files?path={os.path.dirname(path)}", status_code=303
    )
