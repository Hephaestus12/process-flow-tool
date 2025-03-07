# app/services/flowchart_service.py
from app.models.flowchart import Flowchart
from app.db.dynamodb import flowchart_table, node_table, edge_table
from fastapi import HTTPException
import json

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
        print("\n" + "="*80)
        print(f"Starting flowchart processing for ID: {flowchart_id}")
        print("="*80 + "\n")

        # 1. Fetch the flowchart from DynamoDB
        print("Step 1: Fetching flowchart from DynamoDB...")
        response = flowchart_table.get_item(Key={"id": flowchart_id})
        if "Item" not in response:
            print(f"❌ Error: Flowchart with ID {flowchart_id} not found")
            raise HTTPException(status_code=404, detail="Flowchart not found")
        flowchart = response["Item"]
        print(f"✅ Successfully fetched flowchart with {len(flowchart.get('nodes', []))} nodes and {len(flowchart.get('edges', []))} edges")

        # 2. Convert decimal to float for easier prompt building
        print("\nStep 2: Converting decimal values to float...")
        nodes = convert_decimal_to_float(flowchart.get("nodes", []))
        edges = convert_decimal_to_float(flowchart.get("edges", []))
        print("✅ Conversion complete")

        # 3. Build a prompt describing the flowchart
        print("\nStep 3: Building LLM prompt...")
        prompt = build_flowchart_prompt(flowchart_id, nodes, edges)
        print("\n📝 Generated Prompt:")
        print("-"*40)
        print(prompt)
        print("-"*40)

        # 4. Call the LLM
        print("\nStep 4: Calling LLM...")
        llm_data = call_llm_for_flowchart(prompt)
        print("\n🤖 LLM Response:")
        print("-"*40)
        print(json.dumps(llm_data, indent=2))
        print("-"*40)

        if isinstance(llm_data, dict) and "error" in llm_data:
            print("\n⚠️ LLM returned an error:")
            print(json.dumps(llm_data, indent=2))
            flowchart["notes"] = llm_data
        else:
            # 5. Merge LLM recommended properties if provided
            print("\nStep 5: Merging LLM recommendations...")
            
            if "nodes" in llm_data:
                print("\n📊 Processing Node Updates:")
                node_updates = llm_data["nodes"]
                updated_nodes_count = 0
                
                # Update each node in the flowchart
                for node in nodes:
                    node_id = str(node["id"])
                    if node_id in node_updates:
                        print(f"\n🔄 Updating Node {node_id}:")
                        # Get the updated node data from LLM
                        updated_node = node_updates[node_id]
                        
                        # Initialize data structure if needed
                        if "data" not in node:
                            node["data"] = {}
                        if "properties" not in node["data"]:
                            node["data"]["properties"] = {}
                        
                        # Update the node's properties
                        if "properties" in updated_node:
                            print(f"  Properties to update: {list(updated_node['properties'].keys())}")
                            for prop_name, prop_data in updated_node["properties"].items():
                                # Only update if the property doesn't exist or is not locked
                                if (prop_name not in node["data"]["properties"] or 
                                    not node["data"]["properties"][prop_name].get("isLocked", False)):
                                    print(f"    ✓ Setting {prop_name} = {prop_data['value']}")
                                    node["data"]["properties"][prop_name] = {
                                        "value": prop_data["value"],
                                        "isLocked": False
                                    }
                                    updated_nodes_count += 1
                
                flowchart["nodes"] = nodes
                print(f"\n✅ Updated {updated_nodes_count} node properties")

            # Update edges if provided
            if "edges" in llm_data:
                print("\n📊 Processing Edge Updates:")
                edge_updates = llm_data["edges"]
                updated_edges_count = 0
                
                for edge in edges:
                    edge_id = str(edge["id"])
                    if edge_id in edge_updates:
                        print(f"\n🔄 Updating Edge {edge_id}:")
                        # Get the updated edge data from LLM
                        updated_edge = edge_updates[edge_id]
                        
                        # Initialize data structure if needed
                        if "data" not in edge:
                            edge["data"] = {}
                        if "properties" not in edge["data"]:
                            edge["data"]["properties"] = {}
                        
                        # Update the edge's properties
                        if "properties" in updated_edge:
                            print(f"  Properties to update: {list(updated_edge['properties'].keys())}")
                            for prop_name, prop_data in updated_edge["properties"].items():
                                # Only update if the property doesn't exist or is not locked
                                if (prop_name not in edge["data"]["properties"] or 
                                    not edge["data"]["properties"][prop_name].get("isLocked", False)):
                                    print(f"    ✓ Setting {prop_name} = {prop_data['value']}")
                                    edge["data"]["properties"][prop_name] = {
                                        "value": prop_data["value"],
                                        "isLocked": False
                                    }
                                    updated_edges_count += 1
                
                flowchart["edges"] = edges
                print(f"\n✅ Updated {updated_edges_count} edge properties")

        # 6. Convert data back to decimals for DynamoDB
        print("\nStep 6: Converting float values back to decimal for DynamoDB...")
        flowchart_with_decimals = convert_floats_to_decimal(flowchart)
        print("✅ Conversion complete")

        # 7. Save updated flowchart
        print("\nStep 7: Saving updated flowchart to DynamoDB...")
        flowchart_table.put_item(Item=flowchart_with_decimals)
        print("✅ Save complete")

        print("\n" + "="*80)
        print("Flowchart processing completed successfully!")
        print("="*80 + "\n")
        
        return flowchart
    except Exception as e:
        print("\n❌ Error occurred during flowchart processing:")
        print(f"Error details: {str(e)}")
        print("="*80 + "\n")
        raise HTTPException(status_code=500, detail=str(e))
