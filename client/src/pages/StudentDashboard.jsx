import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { DashboardSidebar } from "../components/dashboard-sidebar";
import { CheckCircle, Clock, TrendingUp, Award, Calendar } from "lucide-react";

export default function StudentDashboard() {
  const { user } = useAuth();

  // Auth protection
  if (!user) return <Navigate to="/login" />;
  if (user.user_metadata.role !== "student") return <Navigate to="/login" />;

  return (
    <div className="min-h-screen bg-background">
      <DashboardSidebar userRole="student" />

      <div className="md:ml-64">
        <div className="p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Welcome back, {user.user_metadata.full_name}!
            </h1>
            <p className="text-muted-foreground">
              Here's your learning progress and upcoming assignments.
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24</div>
                <p className="text-xs text-muted-foreground">Assignments completed</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">Due this week</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Grade</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">89.2%</div>
                <p className="text-xs text-muted-foreground">+3.2% this month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Achievements</CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">7</div>
                <p className="text-xs text-muted-foreground">Badges earned</p>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upcoming Assignments */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Assignments</CardTitle>
                <CardDescription>Your pending assignments and deadlines</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { title: "Math Quiz #4", subject: "Mathematics", due: "Tomorrow", status: "pending" },
                    { title: "Science Lab Report", subject: "Physics", due: "Dec 15", status: "pending" },
                    { title: "History Essay", subject: "World History", due: "Dec 18", status: "pending" },
                  ].map((assignment, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{assignment.title}</h4>
                        <p className="text-sm text-muted-foreground">{assignment.subject}</p>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center text-sm text-muted-foreground mb-2">
                          <Calendar className="h-4 w-4 mr-1" />
                          Due {assignment.due}
                        </div>
                        <Button size="sm">Start</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Results */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Results</CardTitle>
                <CardDescription>Your latest assignment grades and feedback</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { title: "Math Quiz #3", subject: "Mathematics", grade: "95%", feedback: "Excellent work!" },
                    { title: "English Essay", subject: "Literature", grade: "88%", feedback: "Good analysis, minor grammar issues" },
                    { title: "Science Test", subject: "Biology", grade: "92%", feedback: "Strong understanding of concepts" },
                    { title: "History Project", subject: "World History", grade: "85%", feedback: "Well researched, needs more detail" },
                  ].map((result, index) => (
                    <div key={index} className="p-4 bg-muted/50 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium">{result.title}</h4>
                          <p className="text-sm text-muted-foreground">{result.subject}</p>
                        </div>
                        <div
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            Number.parseInt(result.grade) >= 90
                              ? "bg-green-100 text-green-800"
                              : Number.parseInt(result.grade) >= 80
                                ? "bg-blue-100 text-blue-800"
                                : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {result.grade}
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground">{result.feedback}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Progress Chart */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Learning Progress</CardTitle>
              <CardDescription>Your performance across different subjects</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { subject: "Mathematics", progress: 92, color: "bg-blue-500" },
                  { subject: "Science", progress: 88, color: "bg-green-500" },
                  { subject: "History", progress: 85, color: "bg-purple-500" },
                  { subject: "English", progress: 90, color: "bg-orange-500" },
                ].map((subject, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{subject.subject}</span>
                      <span className="text-sm font-medium">{subject.progress}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${subject.color}`}
                        style={{ width: `${subject.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
