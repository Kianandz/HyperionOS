from fastapi import APIRouter
from app.services.metrics import get_system_metrics

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics():

    return get_system_metrics()