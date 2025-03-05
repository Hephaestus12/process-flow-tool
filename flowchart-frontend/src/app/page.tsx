// app/page.tsx
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { v4 as uuidv4 } from "uuid";

const LandingPage: React.FC = () => {
  const router = useRouter();
  const [existingId, setExistingId] = useState("");
  const [showOpen, setShowOpen] = useState(false);

  const handleNewDiagram = () => {
    const newId = uuidv4();
    router.push(`/${newId}`);
  };

  const handleOpenExisting = () => {
    if (existingId.trim() === "") return;
    router.push(`/${existingId.trim()}`);
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold">
            Flowchart Tool
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center space-y-4">
            <Button onClick={handleNewDiagram} className="w-full">
              New Diagram
            </Button>
            <Button
              onClick={() => setShowOpen(true)}
              variant="outline"
              className="w-full"
            >
              Open Existing Diagram
            </Button>
            {showOpen && (
              <div className="w-full space-y-2">
                <Input
                  placeholder="Enter Diagram ID"
                  value={existingId}
                  onChange={(e) => setExistingId(e.target.value)}
                />
                <Button onClick={handleOpenExisting} className="w-full">
                  Open Diagram
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LandingPage;
