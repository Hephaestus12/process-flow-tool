// app/[id]/page.tsx
"use client";

import React from "react";
import { useParams } from "next/navigation";
import FlowchartEditor from "@/components/FlowchartEditor";

const DiagramPage: React.FC = () => {
  const params = useParams();
  const { id } = params;

  if (!id) return <div>Loading...</div>;

  return <FlowchartEditor diagramId={id as string} />;
};

export default DiagramPage;
