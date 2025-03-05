// src/utils/flowchartUtils.ts

export const getDefaultProperties = (nodeType: string) => {
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
