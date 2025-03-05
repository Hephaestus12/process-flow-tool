# app/services/flowchart_service.py
from app.models.flowchart import Flowchart
from app.db.dynamodb import flowchart_table, node_table, edge_table
from fastapi import HTTPException

from app.services.llm_integration import build_flowchart_prompt, call_llm_for_flowchart
from app.utils.decimal_converter import convert_decimal_to_float, convert_floats_to_decimal

def save_flowchart_service(flowchart: Flowchart) -> dict:
    try:
        flowchart_item = flowchart.dict()
        if not flowchart_item.get("id"):
            raise HTTPException(status_code=400, detail="Flowchart 'id' is required.")
        
        # Update each node and edge with the parent flowchart id and verify they have an 'id'
        for node in flowchart_item.get("nodes", []):
            if not node.get("id"):
                raise HTTPException(status_code=400, detail="Each node must have an 'id'.")
            node["flowchart_id"] = flowchart_item["id"]
        for edge in flowchart_item.get("edges", []):
            if not edge.get("id"):
                raise HTTPException(status_code=400, detail="Each edge must have an 'id'.")
            edge["flowchart_id"] = flowchart_item["id"]

        # Convert floats to Decimal (if needed)
        flowchart_item = convert_floats_to_decimal(flowchart_item)
        
        # Save the flowchart metadata
        flowchart_table.put_item(Item=flowchart_item)
        
        # Save each node
        for node in flowchart_item.get("nodes", []):
            node_table.put_item(Item=node)
        
        # Save each edge
        for edge in flowchart_item.get("edges", []):
            edge_table.put_item(Item=edge)
        
        return {"message": "Flowchart saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_flowchart_service(flowchart_id: str) -> dict:
    """
    Retrieve a flowchart by its id.
    """
    try:
        response = flowchart_table.get_item(Key={"id": flowchart_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Flowchart not found")
        return response["Item"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_flowchart_service(flowchart_id: str) -> dict:
    """
    Fetches a flowchart, calls an LLM to fill in missing properties, 
    merges recommended properties, and saves updated flowchart back to DynamoDB.
    """
    try:
        # 1. Fetch the flowchart from DynamoDB
        response = flowchart_table.get_item(Key={"id": flowchart_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Flowchart not found")
        flowchart = response["Item"]

        # 2. Convert decimal to float for easier prompt building
        nodes = convert_decimal_to_float(flowchart.get("nodes", []))
        edges = convert_decimal_to_float(flowchart.get("edges", []))

        # 3. Build a prompt describing the flowchart
        prompt = build_flowchart_prompt(flowchart_id, nodes, edges)

        # 4. Call the LLM
        llm_data = call_llm_for_flowchart(prompt)
        if isinstance(llm_data, dict) and "error" in llm_data:
            # If LLM returned an error or invalid JSON, you can handle gracefully
            flowchart["notes"] = llm_data
        else:
            # 5. Merge LLM recommended properties if provided
            # Assume LLM returns something like:
            # {
            #   "nodes": [
            #       {"id": "1741116205110", "recommendations": {"capacity":"1000 L", ...}},
            #       ...
            #   ]
            # }
            if "nodes" in llm_data:
                # build dict of node_id -> recommended props
                recommendations_by_id = {
                    str(n["id"]): n.get("recommendations", {})
                    for n in llm_data["nodes"]
                    if "id" in n
                }
                # apply to local nodes
                for node in nodes:
                    node_id = str(node["id"])
                    if node_id in recommendations_by_id:
                        recs = recommendations_by_id[node_id]
                        # update node's data.properties
                        if "data" in node and "properties" in node["data"]:
                            node["data"]["properties"].update(recs)
                flowchart["nodes"] = nodes

        # 6. Convert data back to decimals for DynamoDB
        flowchart_with_decimals = convert_floats_to_decimal(flowchart)

        # 7. Save updated flowchart
        flowchart_table.put_item(Item=flowchart_with_decimals)
        return flowchart
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
