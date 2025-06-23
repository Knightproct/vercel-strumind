import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import { format } from "date-fns"

interface AnalysisProgressProps {
  job: any
}

export function AnalysisProgress({ job }: AnalysisProgressProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <Clock className="w-4 h-4" />
      case "running":
        return <Clock className="w-4 h-4 animate-spin" />
      case "completed":
        return <CheckCircle className="w-4 h-4" />
      case "failed":
        return <XCircle className="w-4 h-4" />
      case "cancelled":
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "secondary"
      case "running":
        return "default"
      case "completed":
        return "success"
      case "failed":
        return "destructive"
      case "cancelled":
        return "outline"
      default:
        return "secondary"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Analysis Progress</span>
          <Badge variant={getStatusColor(job.status) as any} className="flex items-center gap-1">
            {getStatusIcon(job.status)}
            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{Math.round(job.progress)}%</span>
          </div>
          <Progress value={job.progress} className="w-full" />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Started:</span>
            <p className="font-medium">{job.started_at ? format(new Date(job.started_at), "PPp") : "Not started"}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Completed:</span>
            <p className="font-medium">
              {job.completed_at ? format(new Date(job.completed_at), "PPp") : "In progress"}
            </p>
          </div>
        </div>

        {job.error_message && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
            <p className="text-sm text-destructive font-medium">Error:</p>
            <p className="text-sm text-destructive">{job.error_message}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
