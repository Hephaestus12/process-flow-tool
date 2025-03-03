from pydantic import BaseModel
from typing import List, Dict, Any

class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    type: str = "default"

class Flowchart(BaseModel):
    name: str
    nodes: List[Node]
    edges: List[Edge]
