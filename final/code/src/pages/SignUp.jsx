import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";

const API = import.meta.env.VITE_API_URL;

export default function SignUp() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const f = fullName.trim();
    const u = username.trim();
    const em = email.trim();
    const p = password.trim();
    const c = confirm.trim();

    if (!f || !u || !em || !p || !c) {
      setError("All fields are mandatory.");
      return;
    }

    if (p !== c) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      if (!API) throw new Error("API missing");

      const signupRes = await fetch(`${API}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fullName: f,
          username: u,
          email: em,
          password: p,
        }),
      });

      const signupData = await signupRes.json();
      if (!signupRes.ok) {
        setError(signupData.error || "Signup failed");
        setLoading(false);
        return;
      }

      const signinRes = await fetch(`${API}/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: u, password: p }),
      });

      if (!signinRes.ok) throw new Error("Signin failed");

      const signinData = await signinRes.json();

      localStorage.setItem("user", JSON.stringify(signinData.user));

      window.dispatchEvent(
        new CustomEvent("userChanged", { detail: signinData.user })
      );

      navigate("/studio");
    } catch {
      setError("Server error. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="bg-white/10 p-8 rounded-2xl w-full max-w-md text-white"
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>

        {error && <div className="text-red-400 mb-4">{error}</div>}

        <input
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="w-full p-3 mb-3 rounded bg-white/5"
        />

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-3 mb-3 rounded bg-white/5"
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-3 mb-3 rounded bg-white/5"
        />

        <div className="relative mb-3">
          <input
            type={showPass ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 rounded bg-white/5 pr-10"
          />
          <span
            onClick={() => setShowPass((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
          >
            {showPass ? <EyeOff size={20} /> : <Eye size={20} />}
          </span>
        </div>

        <div className="relative mb-4">
          <input
            type={showConfirm ? "text" : "password"}
            placeholder="Confirm Password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="w-full p-3 rounded bg-white/5 pr-10"
          />
          <span
            onClick={() => setShowConfirm((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
          >
            {showConfirm ? <EyeOff size={20} /> : <Eye size={20} />}
          </span>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-2 rounded font-bold disabled:opacity-60"
        >
          {loading ? "Creating account..." : "Sign Up"}
        </button>
      </form>
    </div>
  );
}
