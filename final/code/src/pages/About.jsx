import React from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Music,
  Smile,
  History,
  Settings,
  TrendingUp,
} from "lucide-react";

const About = () => {
  return (
    <div className="bg-secondary text-white min-h-screen py-12 px-6 font-sans">
      {/* Intro */}
      <section className="max-w-5xl mx-auto text-center mb-16">
        <motion.h1
          className="text-4xl md:text-5xl font-bold mb-6 text-white"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
        >
          About Mood Music AI
        </motion.h1>
        <p className="text-gray-300 text-lg leading-relaxed max-w-3xl mx-auto">
          MuseAI is a next-gen AI-powered music generation platform that
          transforms your <strong>mood</strong> into beautiful melodies.  
          Whether you're feeling happy, calm, energetic, or nostalgic, MuseAI
          adapts to you — creating personalized music like never before.
        </p>
      </section>

      {/* Workflow Diagram */}
      <section className="max-w-6xl mx-auto mb-20">
        <h2 className="text-2xl font-semibold text-center mb-12 text-white">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 items-center text-center">
          <div className="p-4 bg-gray-800 rounded-xl shadow hover:shadow-lg">
            <Smile className="mx-auto mb-2 text-accent" size={36} />
            <p>User shares mood</p>
          </div>
          <div className="text-3xl text-gray-400">➡️</div>
          <div className="p-4 bg-gray-800 rounded-xl shadow hover:shadow-lg">
            <Brain className="mx-auto mb-2 text-accent" size={36} />
            <p>AI analyzes mood</p>
          </div>
          <div className="text-3xl text-gray-400">➡️</div>
          <div className="p-4 bg-gray-800 rounded-xl shadow hover:shadow-lg">
            <Music className="mx-auto mb-2 text-accent" size={36} />
            <p>Generates music</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto mb-20">
        <h2 className="text-2xl font-semibold text-center mb-12 text-white">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { icon: <Smile size={32} />, title: "Mood-based Generation", desc: "Music adapts to your feelings instantly." },
            { icon: <Settings size={32} />, title: "Manual Controls", desc: "Customize tempo, energy, instruments, and more." },
            { icon: <History size={32} />, title: "Personalized History", desc: "Revisit and replay your past creations." },
            { icon: <TrendingUp size={32} />, title: "AI Learning", desc: "Improves with every user interaction." },
            { icon: <Music size={32} />, title: "Preset Ideas", desc: "Start with curated suggestions to spark creativity." },
            { icon: <Brain size={32} />, title: "Smart Recommendations", desc: "Suggests music styles based on your mood trends." },
          ].map((f, i) => (
            <motion.div
              key={i}
              className="p-6 bg-gray-800 rounded-2xl shadow hover:shadow-xl text-center"
              whileHover={{ scale: 1.05 }}
            >
              <div className="text-accent mb-3">{f.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-gray-300 text-sm">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tech Stack */}
      <section className="max-w-5xl mx-auto text-center mb-20">
        <h2 className="text-2xl font-semibold mb-8 text-white">Powered By</h2>
        <div className="flex flex-wrap justify-center gap-10 text-lg font-medium text-gray-300">
          <span className="px-4 py-2 bg-gray-800 rounded-lg shadow">React</span>
          <span className="px-4 py-2 bg-gray-800 rounded-lg shadow"> Python</span>
          <span className="px-4 py-2 bg-gray-800 rounded-lg shadow"> AI/ML Models</span>
          <span className="px-4 py-2 bg-gray-800 rounded-lg shadow"> TailwindCSS</span>
        </div>
      </section>

      {/* Vision */}
      <section className="max-w-4xl mx-auto text-center">
        <motion.h2
          className="text-3xl font-bold mb-6 text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          The Future of Music is Here 
        </motion.h2>
        <p className="text-gray-300 text-lg leading-relaxed">
          At MuseAI, we believe music should be <strong>personal</strong>,
          <strong>adaptive</strong>, and <strong>limitless</strong>.  
          This is not just another streaming platform — it's your personal
          AI composer, always tuned to your emotions.
        </p>
      </section>
    </div>
  );
};

export default About;
