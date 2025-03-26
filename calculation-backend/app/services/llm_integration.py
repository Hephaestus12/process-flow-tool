# app/services/llm_integration.py

import json
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
import os

from app.utils.decimal_converter import convert_decimal_to_float

client = openai.OpenAI(api_key="test_key")


def build_flowchart_prompt(flowchart_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> str:
    node_descriptions = []
    for node in nodes:
        label = node.get("data", {}).get("label", "(no label)")
        properties = node.get("data", {}).get("properties", {})
        locked_props = {k: v for k, v in properties.items() if v.get("isLocked")}
        unlocked_props = {k: v for k, v in properties.items() if not v.get("isLocked")}
        node_descriptions.append(
            f"Node {node['id']} labeled '{label}':\n"
            f"  Locked properties: {locked_props}\n"
            f"  Unlocked properties: {unlocked_props}"
        )

    edge_descriptions = []
    for edge in edges:
        source = edge.get("source", "unknown")
        target = edge.get("target", "unknown")
        properties = edge.get("data", {}).get("properties", {})
        locked_props = {k: v for k, v in properties.items() if v.get("isLocked")}
        unlocked_props = {k: v for k, v in properties.items() if not v.get("isLocked")}
        edge_descriptions.append(
            f"Edge {edge['id']} ({source} --> {target}):\n"
            f"  Locked properties: {locked_props}\n"
            f"  Unlocked properties: {unlocked_props}"
        )

    prompt = f"""
You are an expert chemical process engineer. We have a flowchart with ID: {flowchart_id}.
Nodes are components (tanks, pumps, heat exchangers, etc.) and edges represent pipes between them.

I need you to help me figure out the properties needed for the components and pipes.

Current flowchart state:
Nodes:
{chr(10).join(node_descriptions)}

Edges:
{chr(10).join(edge_descriptions)}

IMPORTANT:
- Locked properties are set and should not be modified
- Only suggest values for unlocked properties
- Do not include any already existing properties
- Output only valid JSON using the schema below

Required output schema:
{{
  "nodes": {{
    "<node_id>": {{
      "properties": {{
        "<property_name>": {{
          "value": "<string>",
          "isLocked": false
        }}
      }}
    }}
  }},
  "edges": {{
    "<edge_id>": {{
      "properties": {{
        "<property_name>": {{
          "value": "<string>",
          "isLocked": false
        }}
      }}
    }}
  }}
}}
"""
    return prompt.strip()

def call_llm_for_flowchart(prompt: str) -> Dict[str, Any]:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a chemical process design assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        llm_text = response.choices[0].message.content.strip()

        if llm_text.startswith("```json"):
            llm_text = llm_text.removeprefix("```json").removesuffix("```").strip()
        elif llm_text.startswith("```"):
            llm_text = llm_text.removeprefix("```").removesuffix("```").strip()

        return json.loads(llm_text)
    except Exception as e:
        return {
            "error": "LLM call or parsing failed",
            "error_details": str(e),
            "raw_response": locals().get("llm_text", None)
        }
    
def apply_llm_recommendations(flowchart: dict) -> dict:
    nodes = convert_decimal_to_float(flowchart.get("nodes", []))
    edges = convert_decimal_to_float(flowchart.get("edges", []))

    prompt = build_flowchart_prompt(flowchart["id"], nodes, edges)
    llm_data = call_llm_for_flowchart(prompt)

    if isinstance(llm_data, dict) and "error" in llm_data:
        flowchart["notes"] = llm_data
        return flowchart

    if "nodes" in llm_data:
        node_updates = llm_data["nodes"]
        for node in nodes:
            node_id = str(node["id"])
            if node_id in node_updates:
                updated_node = node_updates[node_id]
                node.setdefault("data", {}).setdefault("properties", {})
                for prop_name, prop_data in updated_node.get("properties", {}).items():
                    if (prop_name not in node["data"]["properties"] or
                        not node["data"]["properties"][prop_name].get("isLocked", False)):
                        node["data"]["properties"][prop_name] = {
                            "value": prop_data["value"],
                            "isLocked": False
                        }
        flowchart["nodes"] = nodes

    if "edges" in llm_data:
        edge_updates = llm_data["edges"]
        for edge in edges:
            edge_id = str(edge["id"])
            if edge_id in edge_updates:
                updated_edge = edge_updates[edge_id]
                edge.setdefault("data", {}).setdefault("properties", {})
                for prop_name, prop_data in updated_edge.get("properties", {}).items():
                    if (prop_name not in edge["data"]["properties"] or
                        not edge["data"]["properties"][prop_name].get("isLocked", False)):
                        edge["data"]["properties"][prop_name] = {
                            "value": prop_data["value"],
                            "isLocked": False
                        }
        flowchart["edges"] = edges

    return flowchart