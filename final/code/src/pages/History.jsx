import React, { useEffect, useState } from "react";

export default function History() {
  const [items, setItems] = useState([]);

  // useEffect(() => {
  //   // Load history from Studio page
  //   const raw = localStorage.getItem("musicHistory"); // key used in Studio.jsx
  //   const history = raw ? JSON.parse(raw) : [];
  //   setItems(history.reverse()); // show latest first
  // }, []);


  // useEffect(() => {
  //   const username = localStorage.getItem("username") || "guest";
  
  //   fetch(`http://127.0.0.1:8000/get-history/${username}`)
  //     .then(res => res.json())
  //     .then(data => setItems(data.reverse()))
  //     .catch(err => console.error("Failed to load history:", err));
  // }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        // replace 'devika' with actual username if available
        const response = await fetch("http://127.0.0.1:8000/get-history/devika");
        if (!response.ok) throw new Error("Failed to fetch history");
        const data = await response.json();
        setItems(data.reverse());
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };
  
    fetchHistory();
  }, []);
  
  

  return (
    <div className="bg-secondary min-h-screen py-12 px-6 font-sans">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-4 text-white">History & Library</h1>
        <p className="text-gray-300 mb-8">
          Your previously generated tracks and prompts.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.length === 0 ? (
            <p className="text-gray-400 col-span-full text-center">
              No generated tracks yet.
            </p>
          ) : (
            items.map((it, idx) => (
              <div
                key={idx}
                className="relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-shadow duration-300 bg-gradient-to-br from-gray-800/80 to-gray-900/80 backdrop-blur-md p-4 flex flex-col"
              >
                {/* Background Image */}
                <div
                  className="absolute inset-0 bg-cover bg-center opacity-30"
                  style={{
                    backgroundImage: `url(${it.image || `https://source.unsplash.com/400x400/?music,instruments`})`,
                  }}
                ></div>

                {/* Icon */}
                <div className="z-10 flex items-center justify-center h-36 w-full bg-gradient-to-br from-primary/50 to-accent/50 rounded-xl text-white text-4xl font-bold mb-3 shadow-inner">
                  🎵
                </div>

                {/* Info */}
                <div className="z-10 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="font-semibold text-white text-lg">{it.prompt}</div>
                    <div className="text-gray-300 mt-1">
                      <strong>Mood:</strong> {it.mood} | <strong>Instruments:</strong> {it.instruments}
                    </div>
                    <div className="text-gray-400 text-sm mt-1">
                      {it.tempo} BPM • {it.duration}s • {it.timestamp}
                    </div>
                    {it.audioUrl && (
                      <audio
                        controls
                        className="mt-3 w-full rounded bg-gray-900"
                        src={it.audioUrl}
                      ></audio>
                    )}
                  </div>

                  {/* Buttons */}
                  <div className="mt-4 flex gap-2">
                    <button className="flex-1 px-3 py-1 rounded-lg bg-primary hover:bg-primary/80 transition">
                      Play
                    </button>
                    <a
                      href={it.audioUrl}
                      download="music.mp3"
                      className="flex-1 px-3 py-1 rounded-lg bg-gray-700 hover:bg-gray-600 transition text-center"
                    >
                      Export
                    </a>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
