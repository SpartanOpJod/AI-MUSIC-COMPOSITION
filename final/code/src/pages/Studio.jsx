import React, { useState, useEffect } from "react";
import Waveform from "../components/Waveform";

const API = import.meta.env.VITE_API_URL;

export default function Studio() {
  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState(20);
  const [mood, setMood] = useState("Happy");
  const [tempo, setTempo] = useState(120);
  const [instruments, setInstruments] = useState("Piano");
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState("");

  const [history, setHistory] = useState(() =>
    JSON.parse(localStorage.getItem("musicHistory")) || []
  );

  useEffect(() => {
    const savedMood = localStorage.getItem("muse_mood");
    if (savedMood) {
      setMood(savedMood);
      localStorage.removeItem("muse_mood");
    }
  }, []);

  const saveToHistory = (item) => {
    const updated = [item, ...history];
    setHistory(updated);
    localStorage.setItem("musicHistory", JSON.stringify(updated));
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setAudioUrl(null);

    try {
      if (!API) throw new Error("API not configured");

      const res = await fetch(`${API}/studio-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          duration,
          mood,
          tempo,
          instruments,
          username: localStorage.getItem("username") || "guest",
        }),
      });

      if (!res.ok) throw new Error("Generation failed");

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);

      saveToHistory({
        prompt,
        duration,
        mood,
        tempo,
        instruments,
        audioUrl: url,
        timestamp: new Date().toLocaleString(),
      });

    } catch (e) {
      setError("❌ Music generation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem("musicHistory");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-black to-secondary text-white p-8">
      <h1 className="text-4xl font-extrabold text-center mb-6">
        🎼 Mood-based AI Music Studio
      </h1>

      <div className="max-w-4xl mx-auto space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label>Prompt</label>
            <textarea
              className="w-full p-3 rounded bg-gray-800"
              rows="3"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="space-y-4">
            <input type="number" min="5" max="30" value={duration}
              onChange={(e) => setDuration(+e.target.value)}
              className="w-full p-2 rounded bg-gray-800" />

            <input type="number" min="60" max="200" value={tempo}
              onChange={(e) => setTempo(+e.target.value)}
              className="w-full p-2 rounded bg-gray-800" />

            <select value={mood} onChange={(e) => setMood(e.target.value)}
              className="w-full p-2 rounded bg-gray-800">
              <option>Happy</option>
              <option>Sad</option>
              <option>Calm</option>
              <option>Energetic</option>
              <option>Romantic</option>
              <option>Mysterious</option>
            </select>

            <input value={instruments}
              onChange={(e) => setInstruments(e.target.value)}
              className="w-full p-2 rounded bg-gray-800" />
          </div>
        </div>

        <button onClick={handleGenerate} disabled={loading}
          className="w-full py-3 rounded bg-primary text-black font-bold">
          {loading ? "Generating..." : "🎶 Generate Music"}
        </button>

        {error && <p className="text-red-400">{error}</p>}

        {audioUrl && (
          <div className="grid grid-cols-3 gap-6 mt-6">
            <div className="col-span-2 space-y-4">
              <audio controls src={audioUrl} />
              <Waveform audioUrl={audioUrl} />
            </div>
          </div>
        )}

        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">History</h2>
          <button onClick={handleClearHistory}
            className="mb-4 px-3 py-1 bg-red-600 rounded">
            Clear History
          </button>

          {history.map((h, i) => (
            <audio key={i} controls src={h.audioUrl} className="w-full mb-2" />
          ))}
        </div>
      </div>
    </div>
  );
}
