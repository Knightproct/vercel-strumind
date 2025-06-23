import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Download, Eye, TrendingUp, Activity } from "lucide-react"
import { format } from "date-fns"

interface AnalysisResultsProps {
  results: any[]
}

export function AnalysisResults({ results }: AnalysisResultsProps) {
  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Activity className="w-12 h-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Analysis Results</h3>
          <p className="text-muted-foreground text-center">Run an analysis to see results here.</p>
        </CardContent>
      </Card>
    )
  }

  const latestResult = results[0]

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Max Displacement</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{latestResult?.max_displacement?.toFixed(3) || "0.000"} mm</div>
            <p className="text-xs text-muted-foreground">Maximum nodal displacement</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Max Stress</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{latestResult?.max_stress?.toFixed(1) || "0.0"} MPa</div>
            <p className="text-xs text-muted-foreground">Maximum element stress</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Analysis Time</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{latestResult?.analysis_time?.toFixed(2) || "0.00"}s</div>
            <p className="text-xs text-muted-foreground">Computation time</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Results */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="summary" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="displacements">Displacements</TabsTrigger>
              <TabsTrigger value="forces">Forces</TabsTrigger>
              <TabsTrigger value="stresses">Stresses</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Analysis Type</TableHead>
                    <TableHead>Load Case</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell className="font-medium">{result.analysis_type}</TableCell>
                      <TableCell>{result.load_case_id}</TableCell>
                      <TableCell>
                        <Badge variant="success">Completed</Badge>
                      </TableCell>
                      <TableCell>{format(new Date(result.created_at), "PPp")}</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-1" />
                            Export
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent value="displacements">
              <div className="text-center py-8 text-muted-foreground">
                Displacement results visualization would be implemented here
              </div>
            </TabsContent>

            <TabsContent value="forces">
              <div className="text-center py-8 text-muted-foreground">
                Force results visualization would be implemented here
              </div>
            </TabsContent>

            <TabsContent value="stresses">
              <div className="text-center py-8 text-muted-foreground">
                Stress results visualization would be implemented here
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
