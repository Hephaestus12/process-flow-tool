// src/components/FlowchartEditor.tsx
"use client";

import React, { useCallback, useState, useEffect, useRef } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Node,
  Edge,
  ReactFlowInstance,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import Sidebar from "./Sidebar";
import PropertiesPanel from "./PropertiesPanel";
import TitleBar from "./TitleBar";
import { getFlowchart, saveFlowchart, runFlowchart } from "@/api/FlowchartApi";
import { Button } from "@/components/ui/button";
import { getDefaultProperties } from "@/utils/flowchartUtils";

interface GraphDTO {
  id: string;
  nodes: Node[];
  edges: Edge[];
}

interface FlowchartEditorProps {
  diagramId: string;
}

const FlowchartEditor: React.FC<FlowchartEditorProps> = ({ diagramId }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Load existing diagram using the diagramId.
  useEffect(() => {
    async function fetchFlowchart() {
      try {
        const data = await getFlowchart(diagramId);
        if (data) {
          if (data.nodes) setNodes(data.nodes);
          if (data.edges) {
            const processedEdges = data.edges.map((edge: any) => ({
              ...edge,
              markerEnd: edge.markerEnd || {},
              data: edge.data || {},
            }));
            setEdges(processedEdges);
          }
        }
      } catch (error) {
        console.error("Error fetching flowchart:", error);
      }
    }
    fetchFlowchart();
  }, [diagramId, setNodes, setEdges]);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const nodeType = event.dataTransfer.getData("application/reactflow");
      if (!nodeType || !reactFlowInstance || !reactFlowBounds) return;

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

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

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const constructGraphDTO = (): GraphDTO => ({
    id: diagramId,
    nodes,
    edges,
  });

  const handleSave = async () => {
    try {
      const graphDto = constructGraphDTO();
      console.log("Request body for save:", graphDto);
      await saveFlowchart(diagramId, graphDto);
      alert("Flowchart saved!");
    } catch (error) {
      console.error("Error saving flowchart:", error);
    }
  };

  const handleRun = async () => {
    try {
      const graphDto = constructGraphDTO();
      console.log("Request body for run:", graphDto);
      await saveFlowchart(diagramId, graphDto);
      const updated = await runFlowchart(diagramId, graphDto);
      if (updated.nodes) setNodes(updated.nodes);
      if (updated.edges) setEdges(updated.edges);
      alert("Flowchart processed and updated!");
    } catch (error) {
      console.error("Error running flowchart process:", error);
    }
  };

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode(node);
  };

  const updateNodeProperties = (nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const { label, ...props } = newData;
          return {
            ...node,
            data: {
              ...node.data,
              label: label, // store as plain string
              properties: props, // store the rest as objects { value, isLocked }
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
        <TitleBar diagramId={diagramId} onSave={handleSave} />
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
