// src/utils/flowchartUtils.ts
import { PropertyField } from "@/models/PropertyField";
export const getDefaultProperties = (
  nodeType: string
): { [key: string]: PropertyField } => {
  const defaults: { [key: string]: string } = {};
  switch (nodeType) {
    case "tank":
    case "reactor":
      defaults["orientation"] = "";
      defaults["moc"] = "";
      defaults["capacity"] = "";
      defaults["ldRatio"] = "";
      defaults["length"] = "";
      defaults["diameter"] = "";
      defaults["operatingTemperature"] = "";
      defaults["operatingPressure"] = "";
      break;
    case "pump":
      defaults["moc"] = "";
      defaults["capacity"] = "";
      defaults["operatingTemperature"] = "";
      defaults["operatingPressure"] = "";
      break;
    case "heat_exchanger":
      defaults["hotSideMoc"] = "";
      defaults["coldSideMoc"] = "";
      defaults["area"] = "";
      defaults["duty"] = "";
      defaults["operatingTemperature"] = "";
      defaults["operatingPressure"] = "";
      break;
    case "distillation_column":
      defaults["moc"] = "";
      defaults["diameter"] = "";
      defaults["height"] = "";
      defaults["operatingTemperature"] = "";
      defaults["operatingPressure"] = "";
      break;
    default:
      break;
  }
  // Always include a "chemical" property for all components
  defaults["chemical"] = "";

  const result: { [key: string]: PropertyField } = {};
  for (const key in defaults) {
    result[key] = { value: defaults[key], isLocked: false };
  }
  return result;
};
