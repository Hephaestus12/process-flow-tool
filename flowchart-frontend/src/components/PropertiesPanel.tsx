// components/PropertiesPanel.tsx
"use client";
import React, { useState, useEffect } from "react";
import { Node } from "reactflow";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface PropertiesPanelProps {
  selectedNode: Node | null;
  updateNodeProperties: (nodeId: string, newProperties: any) => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  updateNodeProperties,
}) => {
  const [formValues, setFormValues] = useState<any>({});

  // Load the selected node's properties into form state
  useEffect(() => {
    if (selectedNode) {
      setFormValues(selectedNode.data.properties);
    }
  }, [selectedNode]);

  if (!selectedNode) {
    return (
      <div className="w-64 p-4 border-l border-gray-200">
        <p>Select a node to edit its properties</p>
      </div>
    );
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormValues((prev: any) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = () => {
    updateNodeProperties(selectedNode.id, formValues);
    alert("Properties saved!");
  };

  // Render input fields based on the selected node type
  const renderInputs = () => {
    const nodeType = selectedNode.data.type;
    let fields: { label: string; name: string }[] = [];
    switch (nodeType) {
      case "tank":
      case "reactor":
        fields = [
          { label: "Orientation", name: "orientation" },
          { label: "MOC", name: "moc" },
          { label: "Capacity", name: "capacity" },
          { label: "L/D Ratio", name: "ldRatio" },
          { label: "Length", name: "length" },
          { label: "Diameter", name: "diameter" },
        ];
        break;
      case "pump":
        fields = [
          { label: "MOC", name: "moc" },
          { label: "Capacity", name: "capacity" },
        ];
        break;
      case "heat_exchanger":
        fields = [
          { label: "Hot Side MOC", name: "hotSideMoc" },
          { label: "Cold Side MOC", name: "coldSideMoc" },
          { label: "Area", name: "area" },
          { label: "Duty", name: "duty" },
        ];
        break;
      case "distillation_column":
        fields = [
          { label: "MOC", name: "moc" },
          { label: "Diameter", name: "diameter" },
          { label: "Height", name: "height" },
        ];
        break;
      default:
        fields = [];
    }

    // Common fields for every component
    const commonFields = [
      { label: "Operating Temperature", name: "operatingTemperature" },
      { label: "Operating Pressure", name: "operatingPressure" },
    ];

    return (
      <>
        {fields.map((field) => (
          <div key={field.name} className="mb-4">
            <Label className="block mb-1">{field.label}:</Label>
            <Input
              type="text"
              name={field.name}
              value={formValues[field.name] || ""}
              onChange={handleChange}
              className="w-full"
            />
          </div>
        ))}
        {commonFields.map((field) => (
          <div key={field.name} className="mb-4">
            <Label className="block mb-1">{field.label}:</Label>
            <Input
              type="text"
              name={field.name}
              value={formValues[field.name] || ""}
              onChange={handleChange}
              className="w-full"
            />
          </div>
        ))}
      </>
    );
  };

  return (
    <div className="w-64 p-4 border-l border-gray-200">
      <h3 className="text-lg font-semibold mb-4">Properties</h3>
      <p className="mb-4">Editing: {selectedNode.data.label}</p>
      {renderInputs()}
      <Button onClick={handleSave}>Save Properties</Button>
    </div>
  );
};

export default PropertiesPanel;
