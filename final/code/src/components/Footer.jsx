import React from "react";

export default function Footer(){
  return (
    <footer className="bg-black/70 text-gray-300 py-6 mt-8">
      <div className="max-w-7xl mx-auto px-6 text-center">
        <div className="mb-3">© {new Date().getFullYear()} MuseAI — Mood-based AI Music</div>
        <div className="text-sm">Built with ❤ • Anime & Instrument visuals • Inspired by Spotify + Netflix</div>
      </div>
    </footer>
  );
}
