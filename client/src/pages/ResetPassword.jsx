import { useState } from "react";
import { supabase } from "../lib/supabase";

export default function ResetPassword() {
  const [password, setPassword] = useState("");

  async function handleUpdate() {
    const { error } = await supabase.auth.updateUser({ password });
    if (error) alert(error.message);
    else alert("Password updated successfully!");
  }

  return (
    <div>
      <input
        type="password"
        placeholder="New Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleUpdate}>Update Password</button>
    </div>
  );
}