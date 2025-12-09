import React, { useState } from 'react'
export default function LoginModal({ open, onClose, onLogin }){
  const [name,setName] = useState('')
  if(!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-full max-w-md p-6 card rounded">
        <h3 className="text-xl font-semibold mb-2">Sign in</h3>
        <input value={name} onChange={(e)=>setName(e.target.value)} className="w-full p-3 rounded bg-black/20 mb-3" placeholder="Display name"/>
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-3 py-1 rounded bg-red-600">Cancel</button>
          <button onClick={()=>{ if(!name) return alert('Enter name'); const u={name}; if(onLogin) onLogin(u) }} className="px-3 py-1 rounded bg-[#19e3a8] text-black">Sign in</button>
        </div>
      </div>
    </div>
  )
}
