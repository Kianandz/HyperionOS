import os, json
from fastapi import Form, Depends, responses
from app.core.security import verify_session
from app.services import files as fm_svc
from . import router


@router.post("/extract")
async def extract_zip(path: str = Form(...), _: str = Depends(verify_session)):
    fm_svc.extract_archive(path)
    return responses.RedirectResponse(
        url=f"/files?path={os.path.dirname(path)}", status_code=303
    )


@router.post("/compress")
async def compress_zip(path: str = Form(...), _: str = Depends(verify_session)):
    full_path = fm_svc.get_safe_path(path)
    fm_svc.compress_items(
        [path], os.path.dirname(path), os.path.basename(full_path) + ".zip"
    )
    return responses.RedirectResponse(
        url=f"/files?path={os.path.dirname(path)}", status_code=303
    )


@router.post("/batch-compress")
async def batch_compress_items(
    paths_json: str = Form(...),
    current_path: str = Form(""),
    zip_name: str = Form("archive.zip"),
    _: str = Depends(verify_session),
):
    fm_svc.compress_items(json.loads(paths_json), current_path, zip_name)
    return responses.RedirectResponse(
        url=f"/files?path={current_path}", status_code=303
    )
