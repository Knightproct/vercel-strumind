"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { authAPI } from "@/lib/api"

interface User {
  id: string
  username: string
  email: string
  full_name: string
  is_superuser: boolean
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      authAPI
        .getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("access_token")
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    const response = await authAPI.login(username, password)
    localStorage.setItem("access_token", response.access_token)
    const userData = await authAPI.getCurrentUser()
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem("access_token")
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, login, logout, isLoading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
