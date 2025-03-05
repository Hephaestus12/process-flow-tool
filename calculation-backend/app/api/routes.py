# app/api/routes.py
from fastapi import APIRouter
from app.models.flowchart import Flowchart
from app.services.flowchart_service import (
    save_flowchart_service,
    get_flowchart_service,
    run_flowchart_service
)

router = APIRouter()

@router.post("/flowchart/{flowchart_id}")
def save_flowchart(flowchart_id: str, flowchart: Flowchart):
    return save_flowchart_service(flowchart)

@router.get("/flowchart/{flowchart_id}")
def get_flowchart(flowchart_id: str):
    return get_flowchart_service(flowchart_id)

@router.post("/flowchart/{flowchart_id}/run")
def run_flowchart(flowchart_id: str):
    return run_flowchart_service(flowchart_id)
