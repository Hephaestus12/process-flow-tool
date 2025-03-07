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
import { ensurePropertyFields } from "@/utils/propertyUtils";

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
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);

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
              data: {
                ...edge.data,
                properties: Object.entries(edge.data?.properties || {}).reduce(
                  (acc, [key, value]: [string, any]) => ({
                    ...acc,
                    [key]:
                      typeof value === "object" && value !== null
                        ? value
                        : { value: value || "", isLocked: false },
                  }),
                  {}
                ),
              },
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
    nodes: nodes.map((node) => ({
      ...node,
      data: {
        ...node.data,
        properties: node.data?.properties || {},
      },
    })),
    edges: edges.map((edge) => ({
      ...edge,
      data: {
        ...edge.data,
        properties: edge.data?.properties || {},
      },
    })),
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
      const response = await runFlowchart(diagramId, graphDto);

      // Process and update nodes
      if (response.nodes) {
        setNodes(response.nodes);
      }

      // Process and update edges
      if (response.edges) {
        const processedEdges = response.edges.map((edge: any) => ({
          ...edge,
          markerEnd: edge.markerEnd || {},
          data: {
            ...edge.data,
            properties: Object.entries(edge.data?.properties || {}).reduce(
              (acc, [key, value]: [string, any]) => ({
                ...acc,
                [key]:
                  typeof value === "object" && value !== null
                    ? value
                    : { value: value || "", isLocked: false },
              }),
              {}
            ),
          },
        }));
        setEdges(processedEdges);
      }

      alert("Flowchart processed and updated!");
    } catch (error) {
      console.error("Error running flowchart process:", error);
    }
  };

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  };

  const onEdgeClick = (_: any, edge: Edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  };

  const updateNodeProperties = (nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const label =
            typeof newData.label === "string"
              ? newData.label
              : String(newData.label?.value || "");
          // Remove 'label' from newData; the rest belong to properties.
          const { label: _ignore, ...props } = newData;
          return {
            ...node,
            data: {
              ...node.data,
              label,
              properties: props,
            },
          };
        }
        return node;
      })
    );
  };

  const updateEdgeProperties = (edgeId: string, newData: any) => {
    setEdges((eds) =>
      eds.map((edge) => {
        if (edge.id === edgeId) {
          return {
            ...edge,
            data: {
              ...edge.data,
              properties: newData,
            },
          };
        }
        return edge;
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
            setEdges((eds) =>
              addEdge(
                {
                  ...connection,
                  data: {
                    properties: {
                      chemical: { value: "", isLocked: false },
                      material: { value: "", isLocked: false },
                      diameter: { value: "", isLocked: false },
                      length: { value: "", isLocked: false },
                      flowRate: { value: "", isLocked: false },
                      temperature: { value: "", isLocked: false },
                      pressure: { value: "", isLocked: false },
                      insulation: { value: "", isLocked: false },
                      insulationThickness: { value: "", isLocked: false },
                    },
                  },
                },
                eds
              )
            )
          }
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onEdgeClick={onEdgeClick}
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
        selectedEdge={selectedEdge}
        updateNodeProperties={updateNodeProperties}
        updateEdgeProperties={updateEdgeProperties}
      />
    </div>
  );
};

export default FlowchartEditor;
