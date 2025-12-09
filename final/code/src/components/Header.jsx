import React, { useState, useEffect } from "react";
import { NavLink, Link, useNavigate } from "react-router-dom";

export default function Header() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const nav = [
    { name: "Home", to: "/" },
    { name: "Studio", to: "/studio" },
    { name: "About", to: "/about" },
    { name: "History", to: "/history" },
    { name: "Profile", to: "/profile" },
  ];

  useEffect(() => {
    // initial load
    const storedUser = JSON.parse(localStorage.getItem("user"));
    if (storedUser) setUser(storedUser);

    // listen for login/logout from other parts of the app
    const onUserChanged = (e) => {
      const u = e?.detail ?? JSON.parse(localStorage.getItem("user"));
      setUser(u || null);
    };

    window.addEventListener("userChanged", onUserChanged);
    return () => window.removeEventListener("userChanged", onUserChanged);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("muse_loggedin");
    setUser(null);
    // notify other components
    window.dispatchEvent(new CustomEvent("userChanged", { detail: null }));
    navigate("/signin");
  };

  return (
    <header className="sticky top-0 z-50 bg-black/60 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent2)] flex items-center justify-center text-black font-bold">
            M
          </div>
          <div className="text-lg font-semibold">
            Mood Music AI <span className="text-sm text-gray-400 ml-2">Mood Studio</span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          {nav.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "text-white underline" : "text-gray-300 hover:text-white"
              }
            >
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="text-gray-200 text-sm">Hi, {user.fullName || user.name || user.username}</span>
              <button
                onClick={handleLogout}
                className="px-3 py-1 rounded bg-red-600 text-white text-sm hover:bg-red-700"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/signin"
                className="px-3 py-1 rounded bg-white/5 text-sm hover:bg-white/10"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-3 py-1 rounded bg-gradient-to-br from-[var(--accent)] to-[var(--accent2)] text-black text-sm font-medium"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
