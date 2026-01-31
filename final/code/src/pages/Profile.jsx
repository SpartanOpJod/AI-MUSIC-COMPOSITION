import React, { useState } from "react";
import { User, Music, Calendar, Heart, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const navigate = useNavigate();

  const storedUser = JSON.parse(localStorage.getItem("user"));

  // 🔒 HARD AUTH GUARD
  if (!storedUser) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white bg-secondary">
        <p>Please log in to view your profile.</p>
      </div>
    );
  }

  const musicHistory =
    JSON.parse(localStorage.getItem("musicHistory")) || [];

  const [user, setUser] = useState({
    fullName: storedUser.fullName,
    email: storedUser.email || "Not provided",
    favoriteMood: storedUser.favoriteMood || "Happy",
    joined: storedUser.joined || new Date().toISOString().split("T")[0],
    totalTracks: musicHistory.length,
  });

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: user.fullName,
    email: user.email,
    favoriteMood: user.favoriteMood,
  });

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSave = () => {
    const updatedUser = { ...user, ...formData };
    setUser(updatedUser);

    // ✅ SINGLE SOURCE OF TRUTH
    localStorage.setItem("user", JSON.stringify(updatedUser));

    setIsEditing(false);
  };

  return (
    <div className="bg-secondary min-h-screen font-sans text-white px-6 py-12">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Greeting */}
        <div className="text-2xl mb-6">
          <span className="text-gray-400">Hello, </span>
          <span className="font-bold">{user.fullName}!</span>
        </div>

        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <h1 className="text-4xl font-bold">Profile</h1>
          <button
            onClick={() => setIsEditing(true)}
            className="bg-primary px-6 py-2 rounded-lg font-semibold hover:bg-primary/80 transition"
          >
            Edit Profile
          </button>
        </div>

        {/* User Info */}
        <div className="bg-gray-800 rounded-2xl p-8 flex flex-col md:flex-row items-center md:justify-between shadow-lg">
          <div className="flex items-center gap-6 mb-6 md:mb-0">
            <div className="bg-primary/20 p-6 rounded-full">
              <User size={48} />
            </div>
            <div>
              <h2 className="text-2xl font-bold">{user.fullName}</h2>
              <p className="text-gray-300">{user.email}</p>
              <p className="text-gray-400 text-sm">
                Joined: {user.joined}
              </p>
            </div>
          </div>

          <div className="flex gap-8">
            <div className="text-center">
              <p className="text-xl font-bold">{user.totalTracks}</p>
              <p className="text-gray-400 text-sm">Tracks Generated</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold">{user.favoriteMood}</p>
              <p className="text-gray-400 text-sm">Favorite Mood</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div
            onClick={() => navigate("/studio")}
            className="cursor-pointer bg-gray-800 rounded-2xl p-6 flex flex-col items-center shadow hover:shadow-xl"
          >
            <Music size={36} className="text-primary mb-2" />
            <p>My Tracks</p>
          </div>

          <div
            onClick={() => navigate("/history")}
            className="cursor-pointer bg-gray-800 rounded-2xl p-6 flex flex-col items-center shadow hover:shadow-xl"
          >
            <Calendar size={36} className="text-primary mb-2" />
            <p>History</p>
          </div>

          <div className="bg-gray-800 rounded-2xl p-6 flex flex-col items-center opacity-60">
            <Heart size={36} className="text-accent mb-2" />
            <p>Favorites</p>
          </div>

          <div className="bg-gray-800 rounded-2xl p-6 flex flex-col items-center opacity-60">
            <User size={36} className="text-accent mb-2" />
            <p>Settings</p>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-2xl p-8 w-full max-w-md relative">
            <button
              onClick={() => setIsEditing(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X size={24} />
            </button>

            <h2 className="text-2xl font-bold mb-4">Edit Profile</h2>

            <div className="flex flex-col gap-4">
              <input
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                className="p-3 rounded bg-gray-800"
              />
              <input
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="p-3 rounded bg-gray-800"
              />
              <input
                name="favoriteMood"
                value={formData.favoriteMood}
                onChange={handleChange}
                className="p-3 rounded bg-gray-800"
              />
              <button
                onClick={handleSave}
                className="bg-primary py-2 rounded font-semibold"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
