from app.services import node
from . import router


@router.get("/api/logs/{name}")
async def api_logs(name: str):
    logs = node.get_project_logs(name)
    return {"logs": logs}
