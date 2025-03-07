import { PropertyField } from "@/models/PropertyField";

export function ensurePropertyFields(props: any): any {
  const newProps: any = {};
  for (const key in props) {
    const prop = props[key];
    if (
      prop &&
      typeof prop === "object" &&
      "value" in prop &&
      "isLocked" in prop
    ) {
      newProps[key] = prop;
    } else {
      newProps[key] = new PropertyField(String(prop || ""), false);
    }
  }
  return newProps;
}
