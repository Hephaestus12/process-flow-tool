from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Node(BaseModel):
    id: str
    # Node type (e.g., "default", "input", "output")
    type: Optional[str] = "default"
    # The x and y position on the canvas.
    position: Dict[str, float]
    # Data to be used by the node (e.g., label and additional metadata)
    data: Dict[str, Any]
    # Optional dimensions (width and height) for the node
    width: Optional[float] = None
    height: Optional[float] = None
    # Optional styling information
    style: Optional[Dict[str, Any]] = None
    # Optional CSS class name
    className: Optional[str] = None
    # Optional positions for connecting edges
    sourcePosition: Optional[str] = None
    targetPosition: Optional[str] = None
    # Flags for interactivity
    draggable: Optional[bool] = True
    selectable: Optional[bool] = True
    # New: reference to the parent flowchart id
    flowchart_id: Optional[str] = None

class Edge(BaseModel):
    id: str
    source: str
    # Optional handle id on the source node
    sourceHandle: Optional[str] = None
    target: str
    # Optional handle id on the target node
    targetHandle: Optional[str] = None
    # Edge type (e.g., "default", "smoothstep", etc.)
    type: Optional[str] = "default"
    # Optional animated flag for the edge
    animated: Optional[bool] = False
    # Optional label for the edge
    label: Optional[str] = None
    # Optional styling for the edge
    style: Optional[Dict[str, Any]] = None
    # Optional extra data
    data: Optional[Dict[str, Any]] = None
    # Optional marker configuration for the end of the edge
    markerEnd: Optional[Dict[str, Any]] = None
    # New: reference to the parent flowchart id
    flowchart_id: Optional[str] = None

class Flowchart(BaseModel):
    # Unique identifier for the diagram (e.g., a UUID)
    id: str
    nodes: List[Node]
    edges: List[Edge]
