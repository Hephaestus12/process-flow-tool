# app/services/llm_integration.py

import os
import openai
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in .env or environment variables.")

def build_flowchart_prompt(flowchart_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> str:
    """
    Create a textual prompt describing the flowchart. 
    We'll list nodes and edges, and ask the LLM to fill in missing properties.
    """
    node_descriptions = []
    for node in nodes:
        label = "(no label)"
        if "data" in node and "label" in node["data"]:
            label = node["data"]["label"]
        node_descriptions.append(
            f"Node {node['id']} labeled '{label}' - type: {node.get('type','default')} - properties: {node['data'].get('properties',{})}"
        )

    edge_descriptions = []
    for edge in edges:
        source = edge.get("source", "unknown")
        target = edge.get("target", "unknown")
        edge_descriptions.append(f"Edge {edge['id']}: {source} --> {target}")

    prompt = f"""
You are an expert chemical process engineer. We have a flowchart with ID: {flowchart_id}.
Nodes are components (tanks, pumps, heat exchangers, etc.) with some missing properties.
Edges represent pipes between them.

Current flowchart representation:
Nodes:
{chr(10).join(node_descriptions)}

Edges:
{chr(10).join(edge_descriptions)}

Please:
1) Explain in your own words how these components are connected.
2) Suggest missing or default property values for each node's 'properties' field. 
3) Return your answers in JSON format where each node is updated with "data.properties" containing your recommended values 
   under a "recommendations" key or something similar.

Output only valid JSON.
"""
    return prompt

def call_llm_for_flowchart(prompt: str) -> Dict[str, Any]:
    """
    Call the LLM with the given prompt. Expect a JSON response describing recommended updates.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chemical process design assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    llm_text = response.choices[0].message["content"].strip()

    try:
        return json.loads(llm_text)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON from LLM",
            "raw_response": llm_text
        }
