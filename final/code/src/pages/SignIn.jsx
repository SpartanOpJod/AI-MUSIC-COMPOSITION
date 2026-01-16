import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";

const API = import.meta.env.VITE_API_URL || null;

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!username || !password) {
      setError("All fields are mandatory.");
      return;
    }

    try {
      if (!API) {
        setError("API service is not configured.");
        return;
      }
      const res = await fetch(`${API}/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (res.ok) {
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("username", data.user.username);
        window.dispatchEvent(new CustomEvent("userChanged", { detail: data.user }));
        navigate("/studio");
      } else {
        setError(data.error || "Invalid username or password.");
      }
    } catch (err) {
      console.error("SignIn Error:", err);
      setError("Server error: " + (err.message || "try again later"));
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-900">
      <form onSubmit={handleSubmit} className="bg-white/10 p-8 rounded-2xl w-full max-w-md text-white">
        <h2 className="text-2xl font-bold mb-6 text-center">Sign In</h2>
        {error && <div className="text-red-400 mb-4">{error}</div>}

        <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} className="w-full p-3 mb-3 rounded bg-white/5" />

        <div className="relative mb-4">
          <input type={showPass ? "text" : "password"} placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} className="w-full p-3 rounded bg-white/5 pr-10" />
          <span onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-gray-400">
            {showPass ? <EyeOff size={20} /> : <Eye size={20} />}
          </span>
        </div>

        <button type="submit" className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-2 rounded font-bold hover:opacity-90">
          Sign In
        </button>
      </form>
    </div>
  );
}
