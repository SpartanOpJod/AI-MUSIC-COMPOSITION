import React from "react";

export default function FeedbackCard({ quote, user, star=5, img }){
  return (
    <div className="min-w-[260px] p-4 rounded-lg bg-black/40 soft-shadow">
      <div className="flex items-center gap-3">
        <img src={img} alt={user} className="w-10 h-10 rounded-full object-cover"/>
        <div>
          <div className="font-semibold text-white">{user}</div>
          <div className="text-yellow-300">{'★'.repeat(star)}</div>
        </div>
      </div>
      <div className="mt-3 text-gray-100">“{quote}”</div>
    </div>
  );
}
