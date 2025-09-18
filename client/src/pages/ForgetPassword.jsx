import { useState } from "react";
import { supabase } from "../lib/supabase";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");

  async function handleReset() {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: "http://localhost:5173/reset-password"
    });
    if (error) alert(error.message);
    else alert("Check your email for reset link.");
  }

  return (
    <div>
      <input placeholder="Your Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <button onClick={handleReset}>Send Reset Link</button>
    </div>
  );
}