"use client"

import { useState } from "react"
import { useParams } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { analysisAPI, projectsAPI } from "@/lib/api"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AnalysisSettings } from "@/components/analysis/AnalysisSettings"
import { AnalysisResults } from "@/components/analysis/AnalysisResults"
import { AnalysisHistory } from "@/components/analysis/AnalysisHistory"
import { AnalysisProgress } from "@/components/analysis/AnalysisProgress"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { useToast } from "@/components/ui/use-toast"
import { Play, Square } from "lucide-react"

export function AnalysisPage() {
  const { projectId, modelId } = useParams()
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [analysisSettings, setAnalysisSettings] = useState({
    analysis_type: "linear",
    solver_type: "sparse",
    max_iterations: 100,
    convergence_tolerance: 1e-6,
    include_pdelta: false,
    include_geometric_nonlinearity: false,
    include_material_nonlinearity: false,
  })
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectsAPI.getProject(projectId!),
    enabled: !!projectId,
  })

  const { data: models } = useQuery({
    queryKey: ["structural-models", projectId],
    queryFn: () => projectsAPI.getStructuralModels(projectId!),
    enabled: !!projectId,
  })

  const { data: analysisResults, isLoading: resultsLoading } = useQuery({
    queryKey: ["analysis-results", modelId],
    queryFn: () => analysisAPI.getAnalysisResults(modelId!),
    enabled: !!modelId,
  })

  const { data: currentJob } = useQuery({
    queryKey: ["analysis-job", currentJobId],
    queryFn: () => analysisAPI.getAnalysisJob(currentJobId!),
    enabled: !!currentJobId,
    refetchInterval: (data) => {
      // Stop polling when job is complete
      if (data?.status === "completed" || data?.status === "failed" || data?.status === "cancelled") {
        return false
      }
      return 2000 // Poll every 2 seconds
    },
  })

  const runAnalysisMutation = useMutation({
    mutationFn: analysisAPI.runAnalysis,
    onSuccess: (data) => {
      setCurrentJobId(data.id)
      toast({
        title: "Analysis started",
        description: "Your structural analysis has been queued for processing.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to start analysis. Please try again.",
        variant: "destructive",
      })
    },
  })

  const cancelAnalysisMutation = useMutation({
    mutationFn: analysisAPI.cancelAnalysisJob,
    onSuccess: () => {
      setCurrentJobId(null)
      queryClient.invalidateQueries({ queryKey: ["analysis-results", modelId] })
      toast({
        title: "Analysis cancelled",
        description: "The analysis job has been cancelled.",
      })
    },
  })

  const currentModel = models?.find((m: any) => m.id === modelId)

  const handleRunAnalysis = () => {
    if (!modelId) return

    // For demo purposes, we'll use a dummy load case ID
    const request = {
      model_id: modelId,
      load_case_ids: ["dummy-load-case-1"],
      settings: analysisSettings,
      save_results: true,
    }

    runAnalysisMutation.mutate(request)
  }

  const handleCancelAnalysis = () => {
    if (currentJobId) {
      cancelAnalysisMutation.mutate(currentJobId)
    }
  }

  const isAnalysisRunning = currentJob && ["pending", "running"].includes(currentJob.status)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analysis</h1>
          <p className="text-muted-foreground">
            {currentModel?.name} - {project?.name}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {isAnalysisRunning ? (
            <Button variant="destructive" onClick={handleCancelAnalysis} disabled={cancelAnalysisMutation.isPending}>
              <Square className="w-4 h-4 mr-2" />
              Cancel Analysis
            </Button>
          ) : (
            <Button onClick={handleRunAnalysis} disabled={runAnalysisMutation.isPending}>
              <Play className="w-4 h-4 mr-2" />
              Run Analysis
            </Button>
          )}
        </div>
      </div>

      {/* Analysis Progress */}
      {currentJob && <AnalysisProgress job={currentJob} />}

      {/* Main Content */}
      <Tabs defaultValue="settings" className="space-y-4">
        <TabsList>
          <TabsTrigger value="settings">Settings</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="settings">
          <AnalysisSettings
            settings={analysisSettings}
            onSettingsChange={setAnalysisSettings}
            disabled={isAnalysisRunning}
          />
        </TabsContent>

        <TabsContent value="results">
          {resultsLoading ? (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <LoadingSpinner />
              </CardContent>
            </Card>
          ) : (
            <AnalysisResults results={analysisResults || []} />
          )}
        </TabsContent>

        <TabsContent value="history">
          <AnalysisHistory results={analysisResults || []} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
