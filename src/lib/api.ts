import axios from "axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  },
)

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append("username", username)
    formData.append("password", password)

    const response = await api.post("/api/auth/token", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get("/api/auth/me")
    return response.data
  },
}

// Projects API
export const projectsAPI = {
  getProjects: async () => {
    const response = await api.get("/api/projects/")
    return response.data
  },

  getProject: async (projectId: string) => {
    const response = await api.get(`/api/projects/${projectId}`)
    return response.data
  },

  createProject: async (project: any) => {
    const response = await api.post("/api/projects/", project)
    return response.data
  },

  updateProject: async (projectId: string, project: any) => {
    const response = await api.put(`/api/projects/${projectId}`, project)
    return response.data
  },

  deleteProject: async (projectId: string) => {
    const response = await api.delete(`/api/projects/${projectId}`)
    return response.data
  },

  getStructuralModels: async (projectId: string) => {
    const response = await api.get(`/api/projects/${projectId}/models`)
    return response.data
  },

  createStructuralModel: async (projectId: string, model: any) => {
    const response = await api.post(`/api/projects/${projectId}/models`, model)
    return response.data
  },
}

// Analysis API
export const analysisAPI = {
  runAnalysis: async (request: any) => {
    const response = await api.post("/api/analysis/run", request)
    return response.data
  },

  getAnalysisJob: async (jobId: string) => {
    const response = await api.get(`/api/analysis/jobs/${jobId}`)
    return response.data
  },

  getAnalysisResults: async (modelId: string) => {
    const response = await api.get(`/api/analysis/models/${modelId}/results`)
    return response.data
  },

  getAnalysisResultDetail: async (resultId: string) => {
    const response = await api.get(`/api/analysis/results/${resultId}`)
    return response.data
  },

  cancelAnalysisJob: async (jobId: string) => {
    const response = await api.delete(`/api/analysis/jobs/${jobId}`)
    return response.data
  },
}

// Design API
export const designAPI = {
  runDesignChecks: async (request: any) => {
    const response = await api.post("/api/design/check", request)
    return response.data
  },

  getDesignResults: async (modelId: string) => {
    const response = await api.get(`/api/design/models/${modelId}/results`)
    return response.data
  },

  optimizeSections: async (request: any) => {
    const response = await api.post("/api/design/optimize", request)
    return response.data
  },
}

// Materials API
export const materialsAPI = {
  getMaterials: async (modelId: string) => {
    const response = await api.get(`/api/materials/models/${modelId}`)
    return response.data
  },

  createMaterial: async (material: any) => {
    const response = await api.post("/api/materials/", material)
    return response.data
  },

  updateMaterial: async (materialId: string, material: any) => {
    const response = await api.put(`/api/materials/${materialId}`, material)
    return response.data
  },

  deleteMaterial: async (materialId: string) => {
    const response = await api.delete(`/api/materials/${materialId}`)
    return response.data
  },
}

// Sections API
export const sectionsAPI = {
  getSections: async (modelId: string) => {
    const response = await api.get(`/api/sections/models/${modelId}`)
    return response.data
  },

  createSection: async (section: any) => {
    const response = await api.post("/api/sections/", section)
    return response.data
  },

  updateSection: async (sectionId: string, section: any) => {
    const response = await api.put(`/api/sections/${sectionId}`, section)
    return response.data
  },

  deleteSection: async (sectionId: string) => {
    const response = await api.delete(`/api/sections/${sectionId}`)
    return response.data
  },
}

// BIM API
export const bimAPI = {
  getModelGeometry: async (modelId: string) => {
    const response = await api.get(`/api/bim/models/${modelId}/geometry`)
    return response.data
  },

  exportModel: async (modelId: string, format: string) => {
    const response = await api.post(`/api/bim/models/${modelId}/export`, { format })
    return response.data
  },

  updateGeometry: async (modelId: string, geometry: any) => {
    const response = await api.put(`/api/bim/models/${modelId}/geometry`, geometry)
    return response.data
  },
}
