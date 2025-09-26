// import { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import { supabase } from "../lib/supabase";

// import { Button } from "../components/ui/button";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
// import { Input } from "../components/ui/input";
// import { Label } from "../components/ui/label";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
// import { Navbar } from "../components/Navbar";
// import { GraduationCap, User, Mail, Lock, UserCheck } from "lucide-react";

// export default function Signup() {
//   const [fullName, setFullName] = useState("");
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [role, setRole] = useState("student");
//   const navigate = useNavigate();

//   const handleSignup = async (e) => {
//     e.preventDefault();

//     const { error } = await supabase.auth.signUp({
//       email,
//       password,
//       options: {
//         data: {
//           full_name: fullName,
//           role,
//         },
//       },
//     });

//     if (error) {
//       alert("Signup failed: " + error.message);
//       return;
//     }

//     alert("Signup successful! Please login.");
//     navigate("/login");
//   };

//   return (
//     <div className="min-h-screen bg-background">
//       <Navbar />

//       <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
//         <div className="max-w-md mx-auto">
//           {/* Header */}
//           <div className="text-center mb-8">
//             <div className="flex justify-center mb-4">
//               <div className="p-3 bg-primary rounded-xl">
//                 <GraduationCap className="h-8 w-8 text-primary-foreground" />
//               </div>
//             </div>
//             <h1 className="text-3xl font-bold mb-2">Create Your Account</h1>
//             <p className="text-muted-foreground">
//               Join AutoGrader and revolutionize your educational experience
//             </p>
//           </div>

//           {/* Signup Form */}
//           <Card className="shadow-lg border-0 bg-card/50 backdrop-blur">
//             <CardHeader className="space-y-1">
//               <CardTitle className="text-2xl text-center">Sign Up</CardTitle>
//               <CardDescription className="text-center">
//                 Enter your information to create your account
//               </CardDescription>
//             </CardHeader>
//             <CardContent>
//               <form onSubmit={handleSignup} className="space-y-4">
//                 <div className="space-y-2">
//                   <Label htmlFor="fullName">Full Name</Label>
//                   <div className="relative">
//                     <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
//                     <Input
//                       id="fullName"
//                       type="text"
//                       placeholder="Enter your full name"
//                       className="pl-10"
//                       value={fullName}
//                       onChange={(e) => setFullName(e.target.value)}
//                       required
//                     />
//                   </div>
//                 </div>

//                 <div className="space-y-2">
//                   <Label htmlFor="email">Email</Label>
//                   <div className="relative">
//                     <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
//                     <Input
//                       id="email"
//                       type="email"
//                       placeholder="Enter your email"
//                       className="pl-10"
//                       value={email}
//                       onChange={(e) => setEmail(e.target.value)}
//                       required
//                     />
//                   </div>
//                 </div>

//                 <div className="space-y-2">
//                   <Label htmlFor="password">Password</Label>
//                   <div className="relative">
//                     <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
//                     <Input
//                       id="password"
//                       type="password"
//                       placeholder="Create a password"
//                       className="pl-10"
//                       value={password}
//                       onChange={(e) => setPassword(e.target.value)}
//                       required
//                     />
//                   </div>
//                 </div>

//                 <div className="space-y-2">
//                   <Label htmlFor="role">Role</Label>
//                   <Select value={role} onValueChange={(value) => setRole(value)}>
//                     <SelectTrigger>
//                       <div className="flex items-center">
//                         <UserCheck className="h-4 w-4 text-muted-foreground mr-2" />
//                         <SelectValue placeholder="Select your role" />
//                       </div>
//                     </SelectTrigger>
//                     <SelectContent>
//                       <SelectItem value="student">Student</SelectItem>
//                       <SelectItem value="teacher">Teacher</SelectItem>
//                     </SelectContent>
//                   </Select>
//                 </div>

//                 <Button type="submit" className="w-full" size="lg">
//                   Create Account
//                 </Button>
//               </form>

//               <div className="mt-6 text-center">
//                 <p className="text-sm text-muted-foreground">
//                   Already have an account?{" "}
//                   <a href="/login" className="text-primary hover:underline font-medium">
//                     Sign in
//                   </a>
//                 </p>
//               </div>
//             </CardContent>
//           </Card>
//         </div>
//       </div>

//       {/* Background decoration */}
//       <div className="fixed inset-0 -z-10 overflow-hidden">
//         <div className="absolute -top-40 -right-32 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
//         <div className="absolute -bottom-40 -left-32 w-80 h-80 bg-secondary/5 rounded-full blur-3xl" />
//       </div>
//     </div>
//   );
// }



import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Navbar } from "../components/Navbar";
import { GraduationCap, User, Mail, Lock, UserCheck } from "lucide-react";

export default function Signup() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role,
        },
      },
    });

    if (error) {
      alert("Signup failed: " + error.message);
      return;
    }

    const user = data.user;
    if (!user) {
      alert("Signup failed: No user returned");
      return;
    }

    // Insert into respective table
    if (role === "student") {
      await supabase.from("students").insert([
        {
          student_id: `STU-${user.id.slice(0, 8)}`, // generate simple unique student_id
          full_name: fullName,
          email,
        },
      ]);
    } else if (role === "teacher") {
      await supabase.from("teachers").insert([
        {
          teacher_id: `TEA-${user.id.slice(0, 8)}`, // generate simple unique teacher_id
          full_name: fullName,
          email,
        },
      ]);
    }

    alert("Signup successful! Please login.");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-primary rounded-xl">
                <GraduationCap className="h-8 w-8 text-primary-foreground" />
              </div>
            </div>
            <h1 className="text-3xl font-bold mb-2">Create Your Account</h1>
            <p className="text-muted-foreground">
              Join AutoGrader and revolutionize your educational experience
            </p>
          </div>

          {/* Signup Form */}
          <Card className="shadow-lg border-0 bg-card/50 backdrop-blur">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl text-center">Sign Up</CardTitle>
              <CardDescription className="text-center">
                Enter your information to create your account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSignup} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="fullName">Full Name</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="fullName"
                      type="text"
                      placeholder="Enter your full name"
                      className="pl-10"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      className="pl-10"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type="password"
                      placeholder="Create a password"
                      className="pl-10"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Select value={role} onValueChange={(value) => setRole(value)}>
                    <SelectTrigger>
                      <div className="flex items-center">
                        <UserCheck className="h-4 w-4 text-muted-foreground mr-2" />
                        <SelectValue placeholder="Select your role" />
                      </div>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="student">Student</SelectItem>
                      <SelectItem value="teacher">Teacher</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button type="submit" className="w-full" size="lg">
                  Create Account
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Already have an account?{" "}
                  <a href="/login" className="text-primary hover:underline font-medium">
                    Sign in
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Background decoration */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-32 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-32 w-80 h-80 bg-secondary/5 rounded-full blur-3xl" />
      </div>
    </div>
  );
}
