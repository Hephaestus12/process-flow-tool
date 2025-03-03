"use client";
import React, { useCallback, useState, useEffect, useRef } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Connection,
  Node,
  Edge,
  ReactFlowInstance,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import Sidebar from "./Sidebar";
import PropertiesPanel from "@/components/PropertiesPanel";
import { getFlowchart, saveFlowchart, runFlowchart } from "@/api/FlowchartApi";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Define a DTO model to represent the graph.
interface GraphDTO {
  name: string;
  nodes: Node[];
  edges: Edge[];
}

const FlowchartEditor = () => {
  // Diagram name state; this name will be used as the identifier.
  const [diagramName, setDiagramName] = useState<string>("Untitled Diagram");

  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Optionally, if you want to load an existing diagram based on the name,
  // you can call getFlowchart here.
  useEffect(() => {
    async function fetchFlowchart() {
      try {
        const data = await getFlowchart(diagramName);
        if (data) {
          if (data.nodes) setNodes(data.nodes);
          if (data.edges) setEdges(data.edges);
        }
      } catch (error) {
        console.error("Error fetching flowchart:", error);
      }
    }
    // For example, only fetch if the diagramName is not the default value.
    if (diagramName !== "Untitled Diagram") {
      fetchFlowchart();
    }
  }, [diagramName, setNodes, setEdges]);

  // Helper: get default properties for a given node type.
  const getDefaultProperties = (nodeType: string) => {
    const commonProperties = {
      operatingTemperature: "",
      operatingPressure: "",
    };
    switch (nodeType) {
      case "tank":
      case "reactor":
        return {
          orientation: "",
          moc: "",
          capacity: "",
          ldRatio: "",
          length: "",
          diameter: "",
          ...commonProperties,
        };
      case "pump":
        return {
          moc: "",
          capacity: "",
          ...commonProperties,
        };
      case "heat_exchanger":
        return {
          hotSideMoc: "",
          coldSideMoc: "",
          area: "",
          duty: "",
          ...commonProperties,
        };
      case "distillation_column":
        return {
          moc: "",
          diameter: "",
          height: "",
          ...commonProperties,
        };
      default:
        return { ...commonProperties };
    }
  };

  // Handle node drop from the sidebar.
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const nodeType = event.dataTransfer.getData("application/reactflow");
      if (!nodeType || !reactFlowInstance || !reactFlowBounds) return;

      // Determine drop position within the canvas.
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      // Create a new node with default properties based on its type.
      const newNode: Node = {
        id: new Date().getTime().toString(),
        type: "default",
        position,
        data: {
          label: nodeType,
          type: nodeType,
          properties: getDefaultProperties(nodeType),
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  // Allow drop over the canvas.
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  // Bundle the flowchart data into a GraphDTO.
  const constructGraphDTO = (): GraphDTO => {
    return {
      name: diagramName,
      nodes,
      edges,
    };
  };

  // Save the flowchart by sending the GraphDTO.
  const handleSave = async () => {
    try {
      const graphDto = constructGraphDTO();
      console.log("Request body for save:", graphDto);
      await saveFlowchart(diagramName, graphDto);
      alert("Flowchart saved!");
    } catch (error) {
      console.error("Error saving flowchart:", error);
    }
  };

  // Run processing by sending the GraphDTO.
  const handleRun = async () => {
    try {
      const graphDto = constructGraphDTO();
      console.log("Request body for run:", graphDto);
      // Optionally, save before running.
      await saveFlowchart(diagramName, graphDto);
      const updated = await runFlowchart(diagramName, graphDto);
      if (updated.nodes) setNodes(updated.nodes);
      if (updated.edges) setEdges(updated.edges);
      alert("Flowchart processed and updated!");
    } catch (error) {
      console.error("Error running flowchart process:", error);
    }
  };

  // When a node is clicked, mark it as selected to open the Properties Panel.
  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode(node);
  };

  // Update node properties from the Properties Panel.
  const updateNodeProperties = (nodeId: string, newProperties: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              properties: newProperties,
            },
          };
        }
        return node;
      })
    );
  };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 relative" ref={reactFlowWrapper}>
        {/* Header with diagram name input */}
        <div className="p-4 border-b border-gray-200 flex items-center space-x-4">
          <label className="font-medium">Diagram Name:</label>
          <Input
            type="text"
            value={diagramName}
            onChange={(e) => setDiagramName(e.target.value)}
            placeholder="Enter diagram name"
            className="max-w-sm"
          />
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={(connection) =>
            setEdges((eds) => addEdge(connection, eds))
          }
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          fitView
        >
          <Background />
        </ReactFlow>
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex space-x-4">
          <Button onClick={handleSave}>Save</Button>
          <Button onClick={handleRun}>Run</Button>
        </div>
      </div>
      <PropertiesPanel
        selectedNode={selectedNode}
        updateNodeProperties={updateNodeProperties}
      />
    </div>
  );
};

export default FlowchartEditor;
