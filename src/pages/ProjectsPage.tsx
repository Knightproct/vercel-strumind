"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { projectsAPI } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Plus, Search, Building, BracketsIcon as Bridge, Factory } from "lucide-react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { CreateProjectDialog } from "@/components/projects/CreateProjectDialog"
import { ProjectCard } from "@/components/projects/ProjectCard"
import { useToast } from "@/components/ui/use-toast"

export function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data: projects, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: projectsAPI.getProjects,
  })

  const createProjectMutation = useMutation({
    mutationFn: projectsAPI.createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      setShowCreateDialog(false)
      toast({
        title: "Project created",
        description: "Your new project has been created successfully.",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create project. Please try again.",
        variant: "destructive",
      })
    },
  })

  const filteredProjects =
    projects?.filter(
      (project: any) =>
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchTerm.toLowerCase()),
    ) || []

  const getProjectTypeIcon = (type: string) => {
    switch (type) {
      case "building":
        return Building
      case "bridge":
        return Bridge
      case "industrial":
        return Factory
      default:
        return Building
    }
  }

  const getProjectTypeBadge = (type: string) => {
    const variants: Record<string, any> = {
      building: "default",
      bridge: "secondary",
      industrial: "outline",
    }
    return variants[type] || "default"
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground">Manage your structural engineering projects</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredProjects.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Building className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No projects found</h3>
            <p className="text-muted-foreground text-center mb-4">
              {searchTerm ? "No projects match your search criteria." : "Get started by creating your first project."}
            </p>
            {!searchTerm && (
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map((project: any) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {/* Create Project Dialog */}
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSubmit={(data) => createProjectMutation.mutate(data)}
        isLoading={createProjectMutation.isPending}
      />
    </div>
  )
}
