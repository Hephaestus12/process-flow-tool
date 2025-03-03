// components/Sidebar.tsx

"use client";
import React from "react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

const nodeTypes = [
  { type: "tank", label: "Tank" },
  { type: "pump", label: "Pump" },
  { type: "heat_exchanger", label: "Heat Exchanger" },
  { type: "reactor", label: "Reactor" },
  { type: "distillation_column", label: "Distillation Column" },
];

const Sidebar = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <aside className="p-4 border-r border-gray-200 w-52">
      <h3 className="text-lg font-semibold mb-4">Components</h3>
      {nodeTypes.map((node) => (
        <Card
          key={node.type}
          onDragStart={(event) => onDragStart(event, node.type)}
          draggable
          className="mb-2 cursor-grab"
        >
          <CardHeader>
            <CardTitle>{node.label}</CardTitle>
          </CardHeader>
        </Card>
      ))}
    </aside>
  );
};

export default Sidebar;
