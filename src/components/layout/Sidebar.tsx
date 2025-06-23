"use client"

import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  FolderOpen,
  CuboidIcon as Cube,
  Calculator,
  Wrench,
  FileText,
  Eye,
  LogOut,
} from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"

interface SidebarProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Projects", href: "/projects", icon: FolderOpen },
]

const modelNavigation = [
  { name: "Model Builder", href: "/builder", icon: Cube },
  { name: "Analysis", href: "/analysis", icon: Calculator },
  { name: "Design", href: "/design", icon: Wrench },
  { name: "Detailing", href: "/detailing", icon: FileText },
  { name: "BIM Viewer", href: "/bim", icon: Eye },
]

export function Sidebar({ open, onOpenChange }: SidebarProps) {
  const location = useLocation()
  const { logout } = useAuth()

  return (
    <>
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-card border-r transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 border-b">
            <h1 className="text-xl font-bold text-primary">StruMind</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {/* Main Navigation */}
            <div className="space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted",
                    )}
                    onClick={() => onOpenChange(false)}
                  >
                    <item.icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                )
              })}
            </div>

            {/* Model Navigation */}
            {location.pathname.includes("/projects/") && location.pathname.includes("/models/") && (
              <div className="pt-6">
                <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Model Tools
                </h3>
                <div className="mt-2 space-y-1">
                  {modelNavigation.map((item) => {
                    const basePath = location.pathname.split("/").slice(0, 5).join("/")
                    const href = basePath + item.href
                    const isActive = location.pathname === href

                    return (
                      <Link
                        key={item.name}
                        to={href}
                        className={cn(
                          "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                          isActive
                            ? "bg-primary text-primary-foreground"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted",
                        )}
                        onClick={() => onOpenChange(false)}
                      >
                        <item.icon className="w-5 h-5 mr-3" />
                        {item.name}
                      </Link>
                    )
                  })}
                </div>
              </div>
            )}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t">
            <Button variant="ghost" className="w-full justify-start" onClick={logout}>
              <LogOut className="w-5 h-5 mr-3" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}
