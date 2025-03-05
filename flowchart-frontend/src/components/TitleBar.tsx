"use client";

import React from "react";
import { useRouter } from "next/navigation";

interface TitleBarProps {
  diagramId: string;
  onSave: () => Promise<void>;
}

const TitleBar: React.FC<TitleBarProps> = ({ diagramId, onSave }) => {
  const router = useRouter();

  const handleClick = async () => {
    try {
      await onSave();
      router.push("/");
    } catch (error) {
      console.error("Error saving diagram on title bar click:", error);
    }
  };

  return (
    <div className="p-4 border-b border-gray-200 flex items-center justify-between">
      <h1 className="text-2xl font-bold cursor-pointer" onClick={handleClick}>
        Process Flow Tool
      </h1>
      <div className="text-lg font-medium">Diagram ID: {diagramId}</div>
    </div>
  );
};

export default TitleBar;
