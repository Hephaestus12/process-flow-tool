"use client";

import React, { useState, useEffect } from "react";
import { Node, Edge } from "reactflow";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface PropertiesPanelProps {
  selectedNode: Node | null;
  selectedEdge: Edge | null;
  updateNodeProperties: (nodeId: string, newData: any) => void;
  updateEdgeProperties: (edgeId: string, newData: any) => void;
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedNode,
  selectedEdge,
  updateNodeProperties,
  updateEdgeProperties,
}) => {
  const [formValues, setFormValues] = useState<any>({});

  // When a node or edge is selected, initialize form state
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
    } else if (selectedEdge) {
      const initialProps = selectedEdge.data?.properties || {};
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
      setFormValues(processedProps);
    }
  }, [selectedNode, selectedEdge]);

  if (!selectedNode && !selectedEdge) {
    return (
      <div className="w-64 p-4 border-l border-gray-200">
        <p>Select a node or pipe to edit its properties</p>
      </div>
    );
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (selectedNode && name === "label") {
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

  const handleLockToggle = (fieldName: string) => {
    setFormValues((prev: any) => ({
      ...prev,
      [fieldName]: { ...prev[fieldName], isLocked: !prev[fieldName].isLocked },
    }));
  };

  const handleSave = () => {
    if (selectedNode) {
      updateNodeProperties(selectedNode.id, formValues);
    } else if (selectedEdge) {
      updateEdgeProperties(selectedEdge.id, formValues);
    }
    alert("Properties saved!");
  };

  const getFields = () => {
    if (selectedNode) {
      let fields: { label: string; name: string }[] = [];
      switch (selectedNode.data.type) {
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
      // Add Chemical as the first property field.
      const extraField = [{ label: "Chemical", name: "chemical" }];
      const commonFields = [
        { label: "Operating Temperature", name: "operatingTemperature" },
        { label: "Operating Pressure", name: "operatingPressure" },
      ];
      return [...extraField, ...fields, ...commonFields];
    } else if (selectedEdge) {
      return [
        { label: "Chemical", name: "chemical" },
        { label: "Material", name: "material" },
        { label: "Diameter", name: "diameter" },
        { label: "Length", name: "length" },
        { label: "Flow Rate", name: "flowRate" },
        { label: "Temperature", name: "temperature" },
        { label: "Pressure", name: "pressure" },
        { label: "Insulation", name: "insulation" },
        { label: "Insulation Thickness", name: "insulationThickness" },
      ];
    }
    return [];
  };

  const fields = getFields();
  const title = selectedNode
    ? `Editing: ${selectedNode.data.label}`
    : "Editing: Pipe";

  return (
    <div className="w-64 p-4 border-l border-gray-200">
      <h3 className="text-lg font-semibold mb-4">Properties</h3>
      <p className="mb-4">{title}</p>
      {selectedNode && (
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
      )}
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
