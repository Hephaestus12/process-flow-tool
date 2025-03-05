// src/components/DiagramHeader.tsx

import React from "react";
import { Input } from "@/components/ui/input";

interface DiagramHeaderProps {
  diagramName: string;
  setDiagramName: (name: string) => void;
}

const DiagramHeader: React.FC<DiagramHeaderProps> = ({
  diagramName,
  setDiagramName,
}) => {
  return (
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
  );
};

export default DiagramHeader;
