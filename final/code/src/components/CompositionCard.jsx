import React from "react";

export default function CompositionCard({ title, img, onUse }){
  return (
    <div className="min-w-[260px] rounded-lg overflow-hidden card-glass soft-shadow">
      <img src={img} alt={title} className="w-full h-44 object-cover"/>
      <div className="p-3">
        <div className="font-semibold">{title}</div>
        <div className="text-sm text-gray-400 mt-1">Mood matched • 30s</div>
        <div className="mt-3 flex gap-2">
          <button className="px-3 py-1 rounded bg-[#3aa0ff]">Preview</button>
          <button onClick={onUse} className="px-3 py-1 rounded bg-[var(--accent)] text-black">Use</button>
        </div>
      </div>
    </div>
  );
}
