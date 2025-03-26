# app/services/flowchart_service.py
from app.models.flowchart import Flowchart
from app.db.dynamodb import flowchart_table, node_table, edge_table
from fastapi import HTTPException
import json

from app.services.llm_integration import apply_llm_recommendations, build_flowchart_prompt, call_llm_for_flowchart
from app.utils.decimal_converter import convert_floats_to_decimal

def save_flowchart_service(flowchart: Flowchart) -> dict:
    try:
        flowchart_item = flowchart.dict()
        if not flowchart_item.get("id"):
            raise HTTPException(status_code=400, detail="Flowchart 'id' is required.")
        
        for node in flowchart_item.get("nodes", []):
            if not node.get("id"):
                raise HTTPException(status_code=400, detail="Each node must have an 'id'.")
            node["flowchart_id"] = flowchart_item["id"]

        for edge in flowchart_item.get("edges", []):
            if not edge.get("id"):
                raise HTTPException(status_code=400, detail="Each edge must have an 'id'.")
            edge["flowchart_id"] = flowchart_item["id"]

        flowchart_item = convert_floats_to_decimal(flowchart_item)
        flowchart_table.put_item(Item=flowchart_item)

        for node in flowchart_item.get("nodes", []):
            node_table.put_item(Item=node)
        for edge in flowchart_item.get("edges", []):
            edge_table.put_item(Item=edge)

        return {"message": "Flowchart saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_flowchart_service(flowchart_id: str) -> dict:
    try:
        response = flowchart_table.get_item(Key={"id": flowchart_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Flowchart not found")
        return response["Item"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_flowchart_service(flowchart_id: str) -> dict:
    try:
        response = flowchart_table.get_item(Key={"id": flowchart_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Flowchart not found")

        flowchart = response["Item"]
        flowchart = apply_llm_recommendations(flowchart)
        updated_flowchart = convert_floats_to_decimal(flowchart)
        flowchart_table.put_item(Item=updated_flowchart)

        return flowchart
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
