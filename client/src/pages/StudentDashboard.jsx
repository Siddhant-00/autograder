import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function StudentDashboard() {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" />;
  if (user.user_metadata.role !== "student") return <Navigate to="/login" />;
  return (
    <div>
      <h1 className=''>Welcome Student {user.user_metadata.full_name}</h1>
    </div>
  )
}