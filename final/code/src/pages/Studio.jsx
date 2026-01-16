// src/pages/Studio.jsx
import React, { useState, useEffect } from "react";
import Waveform from "../components/Waveform";

const API = import.meta.env.VITE_API_URL || null;

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

  // Set mood from localStorage if available (from home page click)
  useEffect(() => {
    const savedMood = localStorage.getItem('muse_mood');
    if (savedMood) {
      setMood(savedMood);
      localStorage.removeItem('muse_mood'); // Clear it after use
    }
  }, []);

  const saveToHistory = (item) => {
    const updated = [item, ...history];
    setHistory(updated);
    localStorage.setItem("musicHistory", JSON.stringify(updated));
  };

  const saveToDB = async (item) => {
    if (!API) {
      console.warn("API URL not configured");
      return;
    }
    try {
      const username = localStorage.getItem("username") || "guest";
      await fetch(`${API}/save-history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...item, username }),
      });
    } catch (err) {
      console.error("Failed to save to DB:", err);
    }
  };
  



  const handleGenerate = async () => {
    if (!API) {
      setError("Backend API is not configured. Please set VITE_API_URL.");
      return;
    }
    setLoading(true);
    setError("");
    setAudioUrl(null);

    try {
      const response = await fetch(`${API}/studio-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, duration, mood, tempo, instruments }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const blob = await response.blob();
      if (!blob.type.startsWith("audio/")) {
        setError("Backend returned non-audio response");
        setLoading(false);
        return;
      }

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
        audioUrl: url,
        timestamp: new Date().toLocaleString(),
      });
      

    } catch (err) {
      setError("❌ Failed to fetch: " + err.message);
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
        {/* Prompt & Controls */}
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label>Prompt / Mood</label>
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
                max="60"
                className="w-full p-2 rounded bg-gray-800 text-white"
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
                className="w-full p-2 rounded bg-gray-800 text-white"
                value={tempo}
                onChange={(e) => setTempo(Number(e.target.value))}
              />
            </div>
            <div>
              <label>Mood</label>
              <select
                className="w-full p-2 rounded bg-gray-800 text-white"
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
                type="text"
                className="w-full p-2 rounded bg-gray-800 text-white"
                value={instruments}
                onChange={(e) => setInstruments(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full py-3 rounded bg-primary text-black font-bold hover:bg-accent transition"
        >
          {loading ? "Generating..." : "🎶 Generate Music"}
        </button>

        {error && <p className="text-red-400">{error}</p>}

        {/* Audio Player + Waveform + Parameters */}
        {audioUrl && (
          <div className="mt-6 grid grid-cols-3 gap-6">
            <div className="col-span-2 space-y-4">
              <audio controls src={audioUrl} className="w-full" />
              <Waveform audioUrl={audioUrl} />
              {/* {audioUrl && <WaveformPlayer audioUrl={audioUrl} />} */}

              {/* <Waveform 
              audioUrl={audioUrl} 
              controls={false}   // hides the audio player
              play={false}       // disables automatic play */}
{/* /> */}

              <a href={audioUrl} download="music.mp3" className="text-accent underline">
                ⬇️ Download MP3
              </a>
            </div>
            <div className="space-y-2 bg-gray-800 p-4 rounded">
              <h3 className="text-lg font-bold">🎵 Music Parameters</h3>
              <p><strong>Mood:</strong> {mood}</p>
              <p><strong>Duration:</strong> {duration} sec</p>
              <p><strong>Tempo:</strong> {tempo} BPM</p>
              <p><strong>Instruments:</strong> {instruments}</p>
            </div>
          </div>
        )}

        {/* History Section */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">🕘 History</h2>
          <button
            onClick={handleClearHistory}
            className="mb-4 py-1 px-3 bg-red-600 rounded hover:bg-red-700"
          >
            Clear History
          </button>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {history.map((item, idx) => (
              <div key={idx} className="grid grid-cols-3 gap-4 p-2 bg-gray-800 rounded">
                <div className="col-span-2">
                  <p><strong>Prompt:</strong> {item.prompt}</p>
                  <audio controls src={item.audioUrl} className="w-full mt-1" />
                  <a href={item.audioUrl} download="music.mp3" className="text-accent underline">
                    ⬇️ Download MP3
                  </a>
                </div>
                <div className="space-y-1">
                  <p><strong>Mood:</strong> {item.mood}</p>
                  <p><strong>Duration:</strong> {item.duration} sec</p>
                  <p><strong>Tempo:</strong> {item.tempo}</p>
                  <p><strong>Instruments:</strong> {item.instruments}</p>
                  <p className="text-sm text-gray-400">{item.timestamp}</p>
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
