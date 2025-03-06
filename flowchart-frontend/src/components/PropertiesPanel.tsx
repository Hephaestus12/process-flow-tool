"use client";

import React, { useState, useEffect } from "react";
import { Node } from "reactflow";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface PropertiesPanelProps {
  selectedNode: Node | null;
  updateNodeProperties: (nodeId: string, newData: any) => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  updateNodeProperties,
}) => {
  const [formValues, setFormValues] = useState<any>({});

  // When a node is selected, set up form state:
  // - 'label' is a plain string.
  // - Other properties are converted to objects { value, isLocked }.
  useEffect(() => {
    if (selectedNode) {
      const initialProps = selectedNode.data.properties || {};
      const processedProps: any = {};
      for (const key in initialProps) {
        const prop = initialProps[key];
        if (
          prop &&
          typeof prop === "object" &&
          "value" in prop &&
          "isLocked" in prop
        ) {
          processedProps[key] = prop;
        } else {
          processedProps[key] = { value: prop || "", isLocked: false };
        }
      }
      setFormValues({
        label: String(selectedNode.data.label || ""),
        ...processedProps,
      });
    }
  }, [selectedNode]);

  if (!selectedNode) {
    return (
      <div className="w-64 p-4 border-l border-gray-200">
        <p>Select a node to edit its properties</p>
      </div>
    );
  }

  // Change handler: treat "label" field separately.
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === "label") {
      setFormValues((prev: any) => ({
        ...prev,
        label: value,
      }));
    } else {
      setFormValues((prev: any) => ({
        ...prev,
        [name]: { ...prev[name], value, isLocked: value.trim() !== "" },
      }));
    }
  };

  // Toggle lock for a given property.
  const handleLockToggle = (fieldName: string) => {
    setFormValues((prev: any) => ({
      ...prev,
      [fieldName]: { ...prev[fieldName], isLocked: !prev[fieldName].isLocked },
    }));
  };

  const handleSave = () => {
    updateNodeProperties(selectedNode.id, formValues);
    alert("Properties saved!");
  };

  // Define property fields based on node type.
  const getFieldsForNodeType = (nodeType: string) => {
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
    const commonFields = [
      { label: "Operating Temperature", name: "operatingTemperature" },
      { label: "Operating Pressure", name: "operatingPressure" },
    ];
    return [...fields, ...commonFields];
  };

  const nodeType = selectedNode.data.type;
  const fields = getFieldsForNodeType(nodeType);

  return (
    <div className="w-64 p-4 border-l border-gray-200">
      <h3 className="text-lg font-semibold mb-4">Properties</h3>
      <p className="mb-4">Editing: {selectedNode.data.label}</p>
      {/* Editable Label Field */}
      <div className="mb-4">
        <Label className="block mb-1">Label:</Label>
        <Input
          type="text"
          name="label"
          value={formValues.label || ""}
          onChange={handleChange}
          className="w-full"
        />
      </div>
      {fields.map((field) => (
        <div key={field.name} className="mb-4 flex items-center space-x-2">
          <div className="flex-1">
            <Label className="block mb-1">{field.label}:</Label>
            <Input
              type="text"
              name={field.name}
              value={formValues[field.name]?.value || ""}
              onChange={handleChange}
              className="w-full"
            />
          </div>
          <div>
            <Label className="block mb-1">Lock</Label>
            <input
              type="checkbox"
              checked={formValues[field.name]?.isLocked || false}
              onChange={() => handleLockToggle(field.name)}
            />
          </div>
        </div>
      ))}
      <Button onClick={handleSave}>Save Properties</Button>
    </div>
  );
};

export default PropertiesPanel;
