# app/services/llm_integration.py

import os
import openai
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(".env.local")
print("Loading environment variables")
print(os.getenv("OPENAI_API_KEY"))
# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_flowchart_prompt(flowchart_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> str:
    """
    Create a textual prompt describing the flowchart. 
    We'll list nodes and edges, and ask the LLM to fill in missing properties.
    """
    print("\n" + "="*80)
    print("Building Flowchart Prompt")
    print("="*80 + "\n")

    # Separate locked and unlocked properties for nodes
    print("📊 Analyzing Node Properties:")
    node_descriptions = []
    for node in nodes:
        label = "(no label)"
        if "data" in node and "label" in node["data"]:
            label = node["data"]["label"]
        
        # Get properties and separate them by locked status
        properties = node["data"].get("properties", {})
        locked_props = {k: v for k, v in properties.items() if v.get("isLocked", False)}
        unlocked_props = {k: v for k, v in properties.items() if not v.get("isLocked", False)}
        
        node_desc = (
            f"Node {node['id']} labeled '{label}':\n"
            f"  Locked properties: {locked_props}\n"
            f"  Unlocked properties: {unlocked_props}"
        )
        node_descriptions.append(node_desc)
        print(f"\n🔄 Node {node['id']}:")
        print(f"  Label: {label}")
        print(f"  Locked properties: {list(locked_props.keys())}")
        print(f"  Unlocked properties: {list(unlocked_props.keys())}")

    # Separate locked and unlocked properties for edges
    print("\n📊 Analyzing Edge Properties:")
    edge_descriptions = []
    for edge in edges:
        source = edge.get("source", "unknown")
        target = edge.get("target", "unknown")
        
        # Get properties and separate them by locked status
        properties = edge.get("data", {}).get("properties", {})
        locked_props = {k: v for k, v in properties.items() if v.get("isLocked", False)}
        unlocked_props = {k: v for k, v in properties.items() if not v.get("isLocked", False)}
        
        edge_desc = (
            f"Edge {edge['id']} ({source} --> {target}):\n"
            f"  Locked properties: {locked_props}\n"
            f"  Unlocked properties: {unlocked_props}"
        )
        edge_descriptions.append(edge_desc)
        print(f"\n🔄 Edge {edge['id']}:")
        print(f"  Source: {source}")
        print(f"  Target: {target}")
        print(f"  Locked properties: {list(locked_props.keys())}")
        print(f"  Unlocked properties: {list(unlocked_props.keys())}")

    prompt = f"""
You are an expert chemical process engineer. We have a flowchart with ID: {flowchart_id}.
Nodes are components (tanks, pumps, heat exchangers, etc.) and edges represent pipes between them.
I am trying to design a chemical process. The flowchart is a representation of the process.
I need you to help me figure out the requirements needed for the properties of the components, and pipes needed to design such a process.
Make sure you use correct units for the properties.(SI units)

Current flowchart state:
Nodes:
{chr(10).join(node_descriptions)}

Edges:
{chr(10).join(edge_descriptions)}

IMPORTANT:
- Locked properties are set in stone and should not be modified
- Only suggest values for unlocked properties
- Do not include any properties that are already set (locked or unlocked)
- Do not include any fields that are not in the schema below

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

Rules:
1. Use exact node and edge IDs from the input
2. Only include properties that need values (unlocked and empty)
3. All property values must be strings
4. All isLocked values must be false
5. Do not include any fields not in the schema
6. Do not include any properties that already have values

Please provide recommendations for values for the unlocked properties.

Output only valid JSON following the exact schema specified above.
"""
    print("\n📝 Generated Prompt:")
    print("-"*40)
    print(prompt)
    print("-"*40 + "\n")
    return prompt

def validate_llm_output(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validates that the LLM output follows our expected schema.
    Returns (is_valid, error_message).
    """
    print("\n🔍 Validating LLM Output:")
    try:
        # Check top-level structure
        if not isinstance(data, dict):
            return False, "Output must be a JSON object"
        
        if "nodes" not in data or "edges" not in data:
            return False, "Output must contain 'nodes' and 'edges' objects"
        
        print("✓ Top-level structure is valid")
        
        # Validate nodes
        print("\n📊 Validating Nodes:")
        for node_id, node_data in data["nodes"].items():
            print(f"\n🔄 Validating Node {node_id}:")
            if not isinstance(node_id, str):
                return False, f"Node ID must be a string, got {type(node_id)}"
            
            if not isinstance(node_data, dict):
                return False, f"Node data must be a JSON object for node {node_id}"
            
            if "properties" not in node_data:
                return False, f"Node {node_id} must contain 'properties' object"
            
            print(f"  ✓ Node structure is valid")
            
            # Validate properties
            for prop_name, prop_data in node_data["properties"].items():
                print(f"  🔍 Validating property: {prop_name}")
                if not isinstance(prop_name, str):
                    return False, f"Property name must be a string in node {node_id}"
                
                if not isinstance(prop_data, dict):
                    return False, f"Property data must be a JSON object for property {prop_name} in node {node_id}"
                
                if "value" not in prop_data or "isLocked" not in prop_data:
                    return False, f"Property {prop_name} in node {node_id} must contain 'value' and 'isLocked'"
                
                if not isinstance(prop_data["value"], str):
                    return False, f"Property value must be a string for property {prop_name} in node {node_id}"
                
                if prop_data["isLocked"] is not False:
                    return False, f"Property isLocked must be false for property {prop_name} in node {node_id}"
                
                print(f"    ✓ Property structure is valid")
        
        # Validate edges
        print("\n📊 Validating Edges:")
        for edge_id, edge_data in data["edges"].items():
            print(f"\n🔄 Validating Edge {edge_id}:")
            if not isinstance(edge_id, str):
                return False, f"Edge ID must be a string, got {type(edge_id)}"
            
            if not isinstance(edge_data, dict):
                return False, f"Edge data must be a JSON object for edge {edge_id}"
            
            if "properties" not in edge_data:
                return False, f"Edge {edge_id} must contain 'properties' object"
            
            print(f"  ✓ Edge structure is valid")
            
            # Validate properties
            for prop_name, prop_data in edge_data["properties"].items():
                print(f"  🔍 Validating property: {prop_name}")
                if not isinstance(prop_name, str):
                    return False, f"Property name must be a string in edge {edge_id}"
                
                if not isinstance(prop_data, dict):
                    return False, f"Property data must be a JSON object for property {prop_name} in edge {edge_id}"
                
                if "value" not in prop_data or "isLocked" not in prop_data:
                    return False, f"Property {prop_name} in edge {edge_id} must contain 'value' and 'isLocked'"
                
                if not isinstance(prop_data["value"], str):
                    return False, f"Property value must be a string for property {prop_name} in edge {edge_id}"
                
                if prop_data["isLocked"] is not False:
                    return False, f"Property isLocked must be false for property {prop_name} in edge {edge_id}"
                
                print(f"    ✓ Property structure is valid")
        
        print("\n✅ Validation completed successfully!")
        return True, ""
    
    except Exception as e:
        print(f"\n❌ Validation error: {str(e)}")
        return False, f"Validation error: {str(e)}"

def fix_llm_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempts to fix common schema issues in the LLM output.
    Returns a new dictionary that matches our expected schema.
    """
    print("\n" + "="*80)
    print("Attempting to Fix LLM Output")
    print("="*80 + "\n")
    
    fixed_data = {
        "nodes": {},
        "edges": {}
    }
    
    try:
        # Fix nodes
        if "nodes" in data:
            print("\n📊 Fixing Node Structure:")
            for node_id, node_data in data["nodes"].items():
                print(f"\n🔄 Processing Node {node_id}:")
                # Convert node_id to string if needed
                node_id = str(node_id)
                
                # Initialize node structure
                fixed_data["nodes"][node_id] = {
                    "properties": {}
                }
                
                # Handle different possible structures
                if isinstance(node_data, dict):
                    # If properties are directly in node_data
                    if "properties" in node_data:
                        props = node_data["properties"]
                    else:
                        props = node_data
                    
                    # Process properties
                    for prop_name, prop_data in props.items():
                        prop_name = str(prop_name)
                        print(f"  🔍 Processing property: {prop_name}")
                        
                        # Handle different property data structures
                        if isinstance(prop_data, dict):
                            # If it's already in the correct format
                            if "value" in prop_data and "isLocked" in prop_data:
                                fixed_data["nodes"][node_id]["properties"][prop_name] = {
                                    "value": str(prop_data["value"]),
                                    "isLocked": False
                                }
                                print(f"    ✓ Property already in correct format")
                            # If it's a simple value
                            elif "value" in prop_data:
                                fixed_data["nodes"][node_id]["properties"][prop_name] = {
                                    "value": str(prop_data["value"]),
                                    "isLocked": False
                                }
                                print(f"    ✓ Fixed property format")
                            # If it's a direct value
                            else:
                                fixed_data["nodes"][node_id]["properties"][prop_name] = {
                                    "value": str(prop_data),
                                    "isLocked": False
                                }
                                print(f"    ✓ Converted direct value to property format")
                        else:
                            # If property data is a direct value
                            fixed_data["nodes"][node_id]["properties"][prop_name] = {
                                "value": str(prop_data),
                                "isLocked": False
                            }
                            print(f"    ✓ Converted direct value to property format")
        
        # Fix edges
        if "edges" in data:
            print("\n📊 Fixing Edge Structure:")
            for edge_id, edge_data in data["edges"].items():
                print(f"\n🔄 Processing Edge {edge_id}:")
                # Convert edge_id to string if needed
                edge_id = str(edge_id)
                
                # Initialize edge structure
                fixed_data["edges"][edge_id] = {
                    "properties": {}
                }
                
                # Handle different possible structures
                if isinstance(edge_data, dict):
                    # If properties are directly in edge_data
                    if "properties" in edge_data:
                        props = edge_data["properties"]
                    else:
                        props = edge_data
                    
                    # Process properties
                    for prop_name, prop_data in props.items():
                        prop_name = str(prop_name)
                        print(f"  🔍 Processing property: {prop_name}")
                        
                        # Handle different property data structures
                        if isinstance(prop_data, dict):
                            # If it's already in the correct format
                            if "value" in prop_data and "isLocked" in prop_data:
                                fixed_data["edges"][edge_id]["properties"][prop_name] = {
                                    "value": str(prop_data["value"]),
                                    "isLocked": False
                                }
                                print(f"    ✓ Property already in correct format")
                            # If it's a simple value
                            elif "value" in prop_data:
                                fixed_data["edges"][edge_id]["properties"][prop_name] = {
                                    "value": str(prop_data["value"]),
                                    "isLocked": False
                                }
                                print(f"    ✓ Fixed property format")
                            # If it's a direct value
                            else:
                                fixed_data["edges"][edge_id]["properties"][prop_name] = {
                                    "value": str(prop_data),
                                    "isLocked": False
                                }
                                print(f"    ✓ Converted direct value to property format")
                        else:
                            # If property data is a direct value
                            fixed_data["edges"][edge_id]["properties"][prop_name] = {
                                "value": str(prop_data),
                                "isLocked": False
                            }
                            print(f"    ✓ Converted direct value to property format")
        
        print("\n✅ Fix completed successfully!")
        return fixed_data
    
    except Exception as e:
        print(f"\n❌ Error during fixing: {str(e)}")
        # If any error occurs during fixing, return the original data
        return data

def fix_llm_output_with_llm(data: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
    """
    Uses the LLM to fix the structure of an invalid response.
    """
    print("\n" + "="*80)
    print("Using LLM to Fix Output Structure")
    print("="*80 + "\n")
    
    fix_prompt = f"""
The previous LLM response was invalid. Please fix the structure to match the required schema.
The current invalid response is:
{json.dumps(data, indent=2)}

The required schema is:
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

Original prompt for context:
{original_prompt}

Please:
1. Extract any valid property values from the invalid response
2. Restructure them to match the required schema
3. Only include properties that were meant to be updated (unlocked and empty)
4. Ensure all values are strings
5. Set all isLocked values to false
6. Use the exact node and edge IDs from the original response

Output only valid JSON following the exact schema specified above.
"""
    
    print("📝 Generated Fix Prompt:")
    print("-"*40)
    print(fix_prompt)
    print("-"*40 + "\n")
    
    try:
        print("🤖 Calling LLM for fix...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a chemical process design assistant."},
                {"role": "user", "content": fix_prompt}
            ],
            temperature=0.0
        )
        fixed_text = response.choices[0].message.content.strip()
        print("\n📥 Received LLM Response:")
        print("-"*40)
        print(fixed_text)
        print("-"*40 + "\n")
        
        fixed_data = json.loads(fixed_text)
        
        # Validate the fixed data
        print("🔍 Validating fixed output...")
        is_valid, error_message = validate_llm_output(fixed_data)
        if is_valid:
            print("✅ Fixed output is valid!")
            return fixed_data
        else:
            print(f"❌ Fixed output is still invalid: {error_message}")
            return {
                "error": "Failed to fix LLM response structure",
                "validation_error": error_message,
                "raw_response": fixed_text
            }
    except Exception as e:
        print(f"❌ Error during LLM fix: {str(e)}")
        return {
            "error": "Error while fixing LLM response structure",
            "error_details": str(e),
            "raw_response": fixed_text if 'fixed_text' in locals() else None
        }

def clean_llm_response(text: str) -> str:
    """
    Cleans the LLM response by removing markdown code blocks, newlines, and other formatting characters.
    """
    print("\n🧹 Cleaning LLM Response:")
    print("Original text:")
    print("-"*40)
    print(text)
    print("-"*40)
    
    # Remove markdown code block markers if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    # Remove leading/trailing whitespace and newlines
    text = text.strip()
    
    print("\nCleaned text:")
    print("-"*40)
    print(text)
    print("-"*40 + "\n")
    
    return text

def call_llm_for_flowchart(prompt: str) -> Dict[str, Any]:
    """
    Call the LLM with the given prompt. Expect a JSON response describing recommended updates.
    """
    print("\n" + "="*80)
    print("Calling LLM for Flowchart")
    print("="*80 + "\n")
    
    print("🤖 Sending prompt to LLM...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chemical process design assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    llm_text = response.choices[0].message.content.strip()
    
    print("\n📥 Received LLM Response:")
    print("-"*40)
    print(llm_text)
    print("-"*40 + "\n")

    try:
        print("🧹 Cleaning response...")
        cleaned_text = clean_llm_response(llm_text)
        
        print("🔍 Parsing JSON response...")
        data = json.loads(cleaned_text)
        print("✓ JSON parsed successfully")
        
        print("\n🔍 Validating response structure...")
        is_valid, error_message = validate_llm_output(data)
        
        if not is_valid:
            print(f"❌ Initial validation failed: {error_message}")
            print("\n🔄 Attempting automatic fix...")
            # Try automatic fixing first
            fixed_data = fix_llm_output(data)
            print("\n🔍 Validating fixed output...")
            is_valid, error_message = validate_llm_output(fixed_data)
            
            if is_valid:
                print("✅ Automatic fix successful!")
                return fixed_data
            else:
                print(f"❌ Automatic fix failed: {error_message}")
                print("\n🔄 Attempting LLM-based fix...")
                # If automatic fixing fails, try using the LLM to fix the structure
                return fix_llm_output_with_llm(data, prompt)
        
        print("✅ Response is valid!")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {str(e)}")
        return {
            "error": "Invalid JSON from LLM",
            "raw_response": llm_text
        }
