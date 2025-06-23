"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"

interface AnalysisSettingsProps {
  settings: any
  onSettingsChange: (settings: any) => void
  disabled?: boolean
}

export function AnalysisSettings({ settings, onSettingsChange, disabled }: AnalysisSettingsProps) {
  const updateSetting = (key: string, value: any) => {
    onSettingsChange({ ...settings, [key]: value })
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Basic Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Type</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="analysis-type">Analysis Type</Label>
            <Select
              value={settings.analysis_type}
              onValueChange={(value) => updateSetting("analysis_type", value)}
              disabled={disabled}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select analysis type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="linear">Linear Static</SelectItem>
                <SelectItem value="nonlinear">Nonlinear Static</SelectItem>
                <SelectItem value="p_delta">P-Delta Analysis</SelectItem>
                <SelectItem value="dynamic">Dynamic Analysis</SelectItem>
                <SelectItem value="modal">Modal Analysis</SelectItem>
                <SelectItem value="buckling">Buckling Analysis</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="solver-type">Solver Type</Label>
            <Select
              value={settings.solver_type}
              onValueChange={(value) => updateSetting("solver_type", value)}
              disabled={disabled}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select solver" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="direct">Direct Solver</SelectItem>
                <SelectItem value="iterative">Iterative Solver</SelectItem>
                <SelectItem value="sparse">Sparse Solver</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="max-iterations">Maximum Iterations</Label>
            <Input
              id="max-iterations"
              type="number"
              value={settings.max_iterations}
              onChange={(e) => updateSetting("max_iterations", Number.parseInt(e.target.value))}
              disabled={disabled}
              min="1"
              max="10000"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="tolerance">Convergence Tolerance</Label>
            <Input
              id="tolerance"
              type="number"
              value={settings.convergence_tolerance}
              onChange={(e) => updateSetting("convergence_tolerance", Number.parseFloat(e.target.value))}
              disabled={disabled}
              step="1e-6"
              min="1e-12"
              max="1e-3"
            />
          </div>
        </CardContent>
      </Card>

      {/* Advanced Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Advanced Options</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="pdelta">P-Delta Effects</Label>
              <p className="text-sm text-muted-foreground">Include second-order effects</p>
            </div>
            <Switch
              id="pdelta"
              checked={settings.include_pdelta}
              onCheckedChange={(checked) => updateSetting("include_pdelta", checked)}
              disabled={disabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="geometric-nonlinearity">Geometric Nonlinearity</Label>
              <p className="text-sm text-muted-foreground">Large displacement analysis</p>
            </div>
            <Switch
              id="geometric-nonlinearity"
              checked={settings.include_geometric_nonlinearity}
              onCheckedChange={(checked) => updateSetting("include_geometric_nonlinearity", checked)}
              disabled={disabled}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="material-nonlinearity">Material Nonlinearity</Label>
              <p className="text-sm text-muted-foreground">Nonlinear material behavior</p>
            </div>
            <Switch
              id="material-nonlinearity"
              checked={settings.include_material_nonlinearity}
              onCheckedChange={(checked) => updateSetting("include_material_nonlinearity", checked)}
              disabled={disabled}
            />
          </div>

          {settings.analysis_type === "dynamic" && (
            <>
              <Separator />
              <div className="space-y-2">
                <Label htmlFor="time-step">Time Step (s)</Label>
                <Input
                  id="time-step"
                  type="number"
                  value={settings.time_step || ""}
                  onChange={(e) => updateSetting("time_step", Number.parseFloat(e.target.value))}
                  disabled={disabled}
                  step="0.001"
                  min="0.001"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="duration">Duration (s)</Label>
                <Input
                  id="duration"
                  type="number"
                  value={settings.duration || ""}
                  onChange={(e) => updateSetting("duration", Number.parseFloat(e.target.value))}
                  disabled={disabled}
                  step="1"
                  min="1"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="damping">Damping Ratio</Label>
                <Input
                  id="damping"
                  type="number"
                  value={settings.damping_ratio || ""}
                  onChange={(e) => updateSetting("damping_ratio", Number.parseFloat(e.target.value))}
                  disabled={disabled}
                  step="0.01"
                  min="0"
                  max="1"
                />
              </div>
            </>
          )}

          {settings.analysis_type === "modal" && (
            <>
              <Separator />
              <div className="space-y-2">
                <Label htmlFor="num-modes">Number of Modes</Label>
                <Input
                  id="num-modes"
                  type="number"
                  value={settings.num_modes || ""}
                  onChange={(e) => updateSetting("num_modes", Number.parseInt(e.target.value))}
                  disabled={disabled}
                  min="1"
                  max="100"
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
