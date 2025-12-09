import React, { useState, useEffect } from "react";
import { User, Music, Calendar, Heart, X } from "lucide-react";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    favoriteMood: "Happy",
  });

  // Load user from localStorage on mount
  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem("user"));
    if (storedUser) {
      setUser({
        fullName: storedUser.fullName,
        email: storedUser.email,
        joined: storedUser.joined || new Date().toISOString().split("T")[0],
        totalTracks: storedUser.totalTracks || 0,
        favoriteMood: storedUser.favoriteMood || "Happy",
      });

      setFormData({
        fullName: storedUser.fullName,
        email: storedUser.email,
        favoriteMood: storedUser.favoriteMood || "Happy",
      });
    }
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = () => {
    const updatedUser = { ...user, ...formData };
    setUser(updatedUser);

    // Update localStorage so Header and Profile stay in sync
    const storedUser = JSON.parse(localStorage.getItem("user")) || {};
    localStorage.setItem(
      "user",
      JSON.stringify({ ...storedUser, ...formData })
    );

    setIsEditing(false);
    alert("Profile updated successfully!");
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white bg-secondary">
        <p>Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="bg-secondary min-h-screen font-sans text-white px-6 py-12">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Greeting */}
        <div className="text-2xl mb-6">
          <span className="text-gray-400">Hello, </span>
          <span className="text-white font-bold">{user.fullName}!</span>
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

        {/* User Info Section */}
        <div className="bg-gray-800 rounded-2xl p-8 flex flex-col md:flex-row items-center md:justify-between shadow-lg hover:shadow-2xl transition">
          <div className="flex items-center gap-6 mb-6 md:mb-0">
            <div className="bg-primary/20 p-6 rounded-full">
              <User size={48} />
            </div>
            <div>
              <h2 className="text-2xl font-bold">{user.fullName}</h2>
              <p className="text-gray-300">{user.email}</p>
              <p className="text-gray-400 text-sm">Joined: {user.joined}</p>
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
          <div className="bg-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center shadow hover:shadow-xl transition">
            <Music size={36} className="text-primary mb-2" />
            <p>My Tracks</p>
          </div>
          <div className="bg-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center shadow hover:shadow-xl transition">
            <Heart size={36} className="text-accent mb-2" />
            <p>Favorites</p>
          </div>
          <div className="bg-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center shadow hover:shadow-xl transition">
            <Calendar size={36} className="text-primary mb-2" />
            <p>History</p>
          </div>
          <div className="bg-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center shadow hover:shadow-xl transition">
            <User size={36} className="text-accent mb-2" />
            <p>Settings</p>
          </div>
        </div>
      </div>

      {/* Edit Profile Modal */}
      {isEditing && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-2xl p-8 w-full max-w-md relative shadow-2xl">
            <button
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
              onClick={() => setIsEditing(false)}
            >
              <X size={24} />
            </button>
            <h2 className="text-2xl font-bold mb-4 text-white">Edit Profile</h2>
            <div className="flex flex-col gap-4">
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="Full Name"
                className="p-3 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email"
                className="p-3 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                type="text"
                name="favoriteMood"
                value={formData.favoriteMood}
                onChange={handleChange}
                placeholder="Favorite Mood"
                className="p-3 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                onClick={handleSave}
                className="bg-primary px-4 py-2 rounded-lg font-semibold hover:bg-primary/80 transition"
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
