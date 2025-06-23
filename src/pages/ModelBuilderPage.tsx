"use client"

import { useState } from "react"
import { useParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { projectsAPI } from "@/lib/api"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ModelCanvas } from "@/components/model-builder/ModelCanvas"
import { NodesPanel } from "@/components/model-builder/NodesPanel"
import { ElementsPanel } from "@/components/model-builder/ElementsPanel"
import { MaterialsPanel } from "@/components/model-builder/MaterialsPanel"
import { SectionsPanel } from "@/components/model-builder/SectionsPanel"
import { LoadsPanel } from "@/components/model-builder/LoadsPanel"
import { ModelToolbar } from "@/components/model-builder/ModelToolbar"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

export function ModelBuilderPage() {
  const { projectId, modelId } = useParams()
  const [selectedTool, setSelectedTool] = useState("select")
  const [selectedElements, setSelectedElements] = useState<string[]>([])

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectsAPI.getProject(projectId!),
    enabled: !!projectId,
  })

  const { data: models, isLoading: modelsLoading } = useQuery({
    queryKey: ["structural-models", projectId],
    queryFn: () => projectsAPI.getStructuralModels(projectId!),
    enabled: !!projectId,
  })

  const currentModel = models?.find((m: any) => m.id === modelId)

  if (projectLoading || modelsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!currentModel) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Model not found</h2>
          <p className="text-muted-foreground">The requested structural model could not be found.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h1 className="text-2xl font-bold">{currentModel.name}</h1>
          <p className="text-muted-foreground">{project?.name}</p>
        </div>
        <ModelToolbar selectedTool={selectedTool} onToolChange={setSelectedTool} modelId={modelId!} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* 3D Canvas */}
        <div className="flex-1 relative">
          <ModelCanvas
            modelId={modelId!}
            selectedTool={selectedTool}
            selectedElements={selectedElements}
            onElementsSelect={setSelectedElements}
          />
        </div>

        {/* Side Panel */}
        <div className="w-80 border-l bg-card">
          <Tabs defaultValue="nodes" className="h-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="nodes">Nodes</TabsTrigger>
              <TabsTrigger value="elements">Elements</TabsTrigger>
              <TabsTrigger value="materials">Materials</TabsTrigger>
              <TabsTrigger value="sections">Sections</TabsTrigger>
              <TabsTrigger value="loads">Loads</TabsTrigger>
            </TabsList>

            <TabsContent value="nodes" className="h-full p-4">
              <NodesPanel modelId={modelId!} selectedElements={selectedElements} />
            </TabsContent>

            <TabsContent value="elements" className="h-full p-4">
              <ElementsPanel modelId={modelId!} selectedElements={selectedElements} />
            </TabsContent>

            <TabsContent value="materials" className="h-full p-4">
              <MaterialsPanel modelId={modelId!} />
            </TabsContent>

            <TabsContent value="sections" className="h-full p-4">
              <SectionsPanel modelId={modelId!} />
            </TabsContent>

            <TabsContent value="loads" className="h-full p-4">
              <LoadsPanel modelId={modelId!} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
