import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { DashboardSidebar } from "../components/dashboard-sidebar";
import { Users, FileText, CheckCircle, Clock, TrendingUp } from "lucide-react";

export default function TeacherDashboard() {
  const { user } = useAuth();

  // Redirect if not logged in
  if (!user) return <Navigate to="/login" />;

  // Redirect if role is not teacher
  if (user.user_metadata.role !== "teacher") return <Navigate to="/login" />;

  return (
    <div className="min-h-screen bg-background">
      <DashboardSidebar userRole="teacher" />

      <div className="md:ml-64">
        <div className="p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Teacher Dashboard
            </h1>
            <p className="text-muted-foreground">
              Welcome back {user.user_metadata.full_name}! Here's an overview of your classes and student progress.
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Students</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">156</div>
                <p className="text-xs text-muted-foreground">+12% from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Assignments</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">23</div>
                <p className="text-xs text-muted-foreground">8 due this week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Graded Today</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">89</div>
                <p className="text-xs text-muted-foreground">+23 from yesterday</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. Grade</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">87.5%</div>
                <p className="text-xs text-muted-foreground">+2.1% from last week</p>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Submissions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Submissions</CardTitle>
                <CardDescription>Latest student assignment submissions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { student: "Alice Johnson", assignment: "Math Quiz #3", time: "2 minutes ago", status: "pending" },
                    { student: "Bob Smith", assignment: "Science Lab Report", time: "15 minutes ago", status: "graded" },
                    { student: "Carol Davis", assignment: "History Essay", time: "1 hour ago", status: "graded" },
                    { student: "David Wilson", assignment: "Math Quiz #3", time: "2 hours ago", status: "pending" },
                  ].map((submission, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <p className="font-medium">{submission.student}</p>
                        <p className="text-sm text-muted-foreground">{submission.assignment}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">{submission.time}</p>
                        <div
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            submission.status === "graded"
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {submission.status === "graded" ? (
                            <>
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Graded
                            </>
                          ) : (
                            <>
                              <Clock className="h-3 w-3 mr-1" />
                              Pending
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Class Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Class Performance</CardTitle>
                <CardDescription>Average scores by subject</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { subject: "Mathematics", score: 92, students: 45 },
                    { subject: "Science", score: 88, students: 42 },
                    { subject: "History", score: 85, students: 38 },
                    { subject: "English", score: 90, students: 41 },
                  ].map((subject, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{subject.subject}</span>
                        <span className="text-sm text-muted-foreground">{subject.students} students</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${subject.score}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">{subject.score}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
