import { useQuery } from "@tanstack/react-query"
import { projectsAPI } from "@/lib/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Link } from "react-router-dom"
import { Plus, FolderOpen, Calculator, Wrench, TrendingUp } from "lucide-react"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { RecentProjects } from "@/components/dashboard/RecentProjects"
import { AnalysisStats } from "@/components/dashboard/AnalysisStats"
import { QuickActions } from "@/components/dashboard/QuickActions"

export function DashboardPage() {
  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: projectsAPI.getProjects,
  })

  const stats = [
    {
      title: "Total Projects",
      value: projects?.length || 0,
      icon: FolderOpen,
      description: "Active structural projects",
    },
    {
      title: "Analyses Run",
      value: "156",
      icon: Calculator,
      description: "This month",
    },
    {
      title: "Design Checks",
      value: "2,341",
      icon: Wrench,
      description: "Elements checked",
    },
    {
      title: "Success Rate",
      value: "98.5%",
      icon: TrendingUp,
      description: "Analysis convergence",
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's an overview of your structural engineering projects.
          </p>
        </div>
        <Button asChild>
          <Link to="/projects">
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Link>
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Projects */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Projects</CardTitle>
              <CardDescription>Your most recently accessed structural projects</CardDescription>
            </CardHeader>
            <CardContent>
              {projectsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner />
                </div>
              ) : (
                <RecentProjects projects={projects?.slice(0, 5) || []} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          <QuickActions />
          <AnalysisStats />
        </div>
      </div>
    </div>
  )
}
