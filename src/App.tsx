import { Routes, Route, Navigate } from "react-router-dom"
import { Toaster } from "@/components/ui/toaster"
import { AuthProvider } from "@/contexts/AuthContext"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { Layout } from "@/components/layout/Layout"
import { LoginPage } from "@/pages/auth/LoginPage"
import { DashboardPage } from "@/pages/DashboardPage"
import { ProjectsPage } from "@/pages/ProjectsPage"
import { ProjectDetailPage } from "@/pages/ProjectDetailPage"
import { ModelBuilderPage } from "@/pages/ModelBuilderPage"
import { AnalysisPage } from "@/pages/AnalysisPage"
import { DesignPage } from "@/pages/DesignPage"
import { DetailingPage } from "@/pages/DetailingPage"
import { BIMViewerPage } from "@/pages/BIMViewerPage"

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/projects" element={<ProjectsPage />} />
                  <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
                  <Route path="/projects/:projectId/models/:modelId/builder" element={<ModelBuilderPage />} />
                  <Route path="/projects/:projectId/models/:modelId/analysis" element={<AnalysisPage />} />
                  <Route path="/projects/:projectId/models/:modelId/design" element={<DesignPage />} />
                  <Route path="/projects/:projectId/models/:modelId/detailing" element={<DetailingPage />} />
                  <Route path="/projects/:projectId/models/:modelId/bim" element={<BIMViewerPage />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
      <Toaster />
    </AuthProvider>
  )
}

export default App
