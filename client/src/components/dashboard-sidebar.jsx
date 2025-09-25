import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "../lib/utils";
import { Button } from "../components/ui/button";
import {
  LayoutDashboard,
  Users,
  FileText,
  BarChart3,
  Settings,
  User,
  GraduationCap,
  Menu,
  X,
} from "lucide-react";

export function DashboardSidebar({ userRole }) {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const teacherNavItems = [
    { href: "/teacher/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/teacher/students", label: "Manage Students", icon: Users },
    { href: "/teacher/assignments", label: "Assignments", icon: FileText },
    { href: "/teacher/results", label: "Results", icon: BarChart3 },
    { href: "/teacher/settings", label: "Settings", icon: Settings },
  ];

  const studentNavItems = [
    { href: "/student/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/student/assignments", label: "My Assignments", icon: FileText },
    { href: "/student/results", label: "Results", icon: BarChart3 },
    { href: "/student/profile", label: "Profile", icon: User },
  ];

  const navItems = userRole === "teacher" ? teacherNavItems : studentNavItems;

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed top-4 left-4 z-50 md:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
      </Button>

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 bg-sidebar border-r border-sidebar-border transform transition-transform duration-200 ease-in-out md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <Link
                          to="/"
                          className="block px-3 py-2 text-foreground hover:text-primary transition-colors"
                          onClick={() => setIsOpen(false)}
                        >
                         
                       
          <div className="flex items-center px-6 py-4 border-b border-sidebar-border">
            <div className="p-2 bg-sidebar-primary rounded-lg">
              <GraduationCap className="h-6 w-6 text-sidebar-primary-foreground" />
            </div>
            <span className="ml-3 text-lg font-bold text-sidebar-foreground">
              AutoGrader
            </span>
          </div>
 </Link>
          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* User info */}
          <div className="px-4 py-4 border-t border-sidebar-border">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-sidebar-primary rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-sidebar-primary-foreground" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-sidebar-foreground">
                  {userRole === "teacher" ? "Teacher" : "Student"}
                </p>
                <p className="text-xs text-sidebar-foreground/60">
                  user@example.com
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
