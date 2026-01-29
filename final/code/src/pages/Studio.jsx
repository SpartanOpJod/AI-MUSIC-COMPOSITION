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

  const [history, setHistory] = useState(() => {
    return JSON.parse(localStorage.getItem("musicHistory")) || [];
  });

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

  const saveToDB = async (item) => {
    if (!API) return;
    try {
      const username = localStorage.getItem("username") || "guest";
      await fetch(`${API}/save-history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...item, username }),
      });
    } catch {}
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setAudioUrl(null);

    try {
      if (!API) throw new Error("Backend API missing");

      const username = localStorage.getItem("username") || "guest";

      const response = await fetch(`${API}/studio-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          duration,
          mood,
          tempo,
          instruments,
          username,
          energy: 5,
        }),
      });

      if (!response.ok) throw new Error("Backend error");

      const blob = await response.blob();
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

      saveToDB({
        prompt,
        duration,
        mood,
        tempo,
        instruments,
      });
    } catch {
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
              className="w-full p-3 rounded bg-gray-800 text-white"
              rows="3"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="space-y-4">
            <div>
              <label>Duration (sec)</label>
              <input
                type="number"
                min="5"
                max="30"
                className="w-full p-2 rounded bg-gray-800"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </div>

            <div>
              <label>Tempo (BPM)</label>
              <input
                type="number"
                min="60"
                max="200"
                className="w-full p-2 rounded bg-gray-800"
                value={tempo}
                onChange={(e) => setTempo(Number(e.target.value))}
              />
            </div>

            <div>
              <label>Mood</label>
              <select
                className="w-full p-2 rounded bg-gray-800"
                value={mood}
                onChange={(e) => setMood(e.target.value)}
              >
                <option>Happy</option>
                <option>Sad</option>
                <option>Calm</option>
                <option>Energetic</option>
                <option>Romantic</option>
                <option>Mysterious</option>
              </select>
            </div>

            <div>
              <label>Main Instrument</label>
              <input
                className="w-full p-2 rounded bg-gray-800"
                value={instruments}
                onChange={(e) => setInstruments(e.target.value)}
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full py-3 rounded bg-primary text-black font-bold"
        >
          {loading ? "Generating..." : "🎶 Generate Music"}
        </button>

        {error && <p className="text-red-400">{error}</p>}

        {audioUrl && (
          <div className="mt-6 grid grid-cols-3 gap-6">
            <div className="col-span-2 space-y-4">
              <audio controls src={audioUrl} className="w-full" />
              <Waveform audioUrl={audioUrl} />
              <a
                href={audioUrl}
                download="music.wav"
                className="text-accent underline"
              >
                ⬇️ Download WAV
              </a>
            </div>

            <div className="bg-gray-800 p-4 rounded space-y-2">
              <p><strong>Mood:</strong> {mood}</p>
              <p><strong>Duration:</strong> {duration}s</p>
              <p><strong>Tempo:</strong> {tempo} BPM</p>
              <p><strong>Instrument:</strong> {instruments}</p>
            </div>
          </div>
        )}

        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">🕘 History</h2>
          <button
            onClick={handleClearHistory}
            className="mb-4 px-3 py-1 bg-red-600 rounded"
          >
            Clear History
          </button>

          <div className="space-y-4 max-h-96 overflow-y-auto">
            {history.map((item, idx) => (
              <div key={idx} className="grid grid-cols-3 gap-4 bg-gray-800 p-2 rounded">
                <div className="col-span-2">
                  <p><strong>Prompt:</strong> {item.prompt}</p>
                  <audio controls src={item.audioUrl} className="w-full mt-1" />
                </div>
                <div className="text-sm space-y-1">
                  <p>Mood: {item.mood}</p>
                  <p>Duration: {item.duration}s</p>
                  <p>Tempo: {item.tempo}</p>
                  <p>{item.timestamp}</p>
                </div>
              </div>
            ))}
            {history.length === 0 && <p>No history yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
