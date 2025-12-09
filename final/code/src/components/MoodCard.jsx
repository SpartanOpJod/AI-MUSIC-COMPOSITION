import React from "react";

export default function MoodCard({ title, image, onClick }){
  return (
    <div
      onClick={onClick}
      className="min-w-[220px] h-56 rounded-lg overflow-hidden relative cursor-pointer soft-shadow"
      role="button"
      title={title}
      style={{ backgroundImage:`url(${image})`, backgroundSize:'cover', backgroundPosition:'center' }}
    >
      <div className="absolute inset-0 bg-black/30"></div>
      <div className="absolute bottom-3 left-3">
        <div className="px-3 py-1 rounded bg-black/60 text-white font-semibold">{title}</div>
      </div>
    </div>
  );
}
