from fastapi import APIRouter, HTTPException
from app.models.flowchart import Flowchart
from app.db.dynamodb import table

router = APIRouter()

@router.post("/flowchart/{name}")
def save_flowchart(name: str, flowchart: Flowchart):
    """
    Save or update a flowchart.
    """
    try:
        table.put_item(Item=flowchart.dict())
        return {"message": "Flowchart saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flowchart/{name}")
def get_flowchart(name: str):
    """
    Retrieve a flowchart by its name.
    """
    response = table.get_item(Key={"name": name})
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Flowchart not found")
    return response["Item"]


@router.post("/flowchart/{name}/run")
def run_flowchart(name: str):
    """
    Process a flowchart. For this example, append ' (processed)' to each node's label.
    """
    response = table.get_item(Key={"name": name})
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Flowchart not found")
    flowchart = response["Item"]

    # Process the flowchart (example: update node label)
    for node in flowchart["nodes"]:
        if "data" in node and "label" in node["data"]:
            node["data"]["label"] += " (processed)"

    table.put_item(Item=flowchart)
    return flowchart
