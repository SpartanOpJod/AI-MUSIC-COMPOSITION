import React from "react";
import { Link } from "react-router-dom";
import { Player } from "@lottiefiles/react-lottie-player";
import CompositionCard from "../components/CompositionCard";
import MoodCard from "../components/MoodCard";
import FeedbackCard from "../components/FeedbackCard";

/*
  Home:
  - Uses high-quality Unsplash images for hero + compositions + moods
  - Lottie animation in hero (music visual)
  - Exactly 10 horizontal composition cards
  - Mood section (10 moods) horizontal
  - Feedback carousel
*/

const COMPS = [
  { id:1, title:'Ocean Breeze', img:'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1400&q=80' },
  { id:2, title:'Night Jazz', img:'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1400&q=80' },
  { id:3, title:'Morning Energy', img:'https://images.unsplash.com/photo-1521335629791-ce4aec67dd47?w=1400&q=80' },
  { id:4, title:'Mystic Piano', img:'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=1400&q=80' },
  { id:5, title:'Nature Calm', img:'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1400&q=80' },
  { id:6, title:'City Lights', img:'https://images.unsplash.com/photo-1508921912186-1d1a45ebb3c1?w=1400&q=80' },
  { id:7, title:'Epic Beats', img:'https://images.unsplash.com/photo-1485579149621-3123dd979885?w=1400&q=80' },
  { id:8, title:'Chill Lo-Fi', img:'https://images.unsplash.com/photo-1513863323964-24f90e58b8d3?w=1400&q=80' },
  { id:9, title:'Happy Vibes', img:'https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=1400&q=80' },
  { id:10, title:'Deep Focus', img:'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?w=1400&q=80' }
];

const MOODS = [
  {title:'Happy', img:'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1200&q=80'},
  {title:'Sad', img:'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=1200&q=80'},
  {title:'Chill', img:'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200&q=80'},
  {title:'Energetic', img:'https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?w=1200&q=80'},
  {title:'Romantic', img:'https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=1200&q=80'},
  {title:'Focus', img:'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=1200&q=80'},
  {title:'Angry', img:'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200&q=80'},
  {title:'Calm', img:'https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=1200&q=80'},
  {title:'Excited', img:'https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=1200&q=80'},
  {title:'Lo-fi', img:'https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?w=1200&q=80'},
];

const FEEDBACKS = [
  {quote:'The music mirrors my feelings perfectly.', user:'Aditi', img:'https://randomuser.me/api/portraits/women/65.jpg'},
  {quote:'Great for focus sessions and studying.', user:'Rahul', img:'https://randomuser.me/api/portraits/men/32.jpg'},
  {quote:'Lovely textures and mood matching.', user:'Kim', img:'https://randomuser.me/api/portraits/women/44.jpg'},
  {quote:'I made a playlist of AI tracks!', user:'John', img:'https://randomuser.me/api/portraits/men/85.jpg'},
];

export default function Home(){
  return (
    <div className="relative min-h-screen text-white">
      {/* Hero */}
      <section className="h-[72vh] relative overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=1600&q=80"
          alt="hero-bg"
          className="absolute inset-0 w-full h-full object-cover opacity-90"
        />
        <div className="absolute inset-0 hero-overlay"></div>

        <div className="relative z-10 max-w-6xl mx-auto px-6 h-full flex flex-col justify-center items-start gap-6">
          <div className="flex items-center gap-6">
            <h1 className="text-6xl font-extrabold leading-tight">Mood Music AI</h1>
            <div className="text-gray-300">— Mood-based AI Music Composition</div>
          </div>

          <p className="max-w-xl text-gray-300">
            Tell MuseAI how you feel and it composes music to match — adjust tempo, instruments, energy and more.
          </p>

          <div className="flex items-center gap-4">
            <Link to="/studio" className="px-6 py-3 rounded-full bg-gradient-to-br from-[#19e3a8] to-[#3aa0ff] text-black font-semibold shadow">
              Try Now
            </Link>
            <a href="#moods" className="px-5 py-3 rounded-full bg-white/5">Explore moods</a>
          </div>
        </div>

        {/* Right-side Lottie animation (music wave) */}
        <div className="absolute right-8 top-12 hidden lg:block w-72">
          <Player
            autoplay
            loop
            src="https://assets9.lottiefiles.com/packages/lf20_2LdLki.json"
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      </section>

      {/* Moods */}
      <section id="moods" className="max-w-6xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold">Choose your mood</h2>
          <div className="text-sm text-gray-400">10 moods • swipe →</div>
        </div>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {MOODS.map((m, i) => (
            <div key={i} className="flex-none">
              <MoodCard
                title={m.title}
                image={m.img}
                onClick={() => { localStorage.setItem('muse_mood', m.title); window.location.href = '/studio'; }}
              />
            </div>
          ))}
        </div>
      </section>

      {/* Featured compositions */}
      <section className="max-w-6xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold">Featured Compositions</h2>
          <div className="text-sm text-gray-400">Curated for moods</div>
        </div>

        <div className="flex gap-4 overflow-x-auto pb-4">
          {COMPS.map((c) => (
            <CompositionCard key={c.id} title={c.title} img={c.img} onUse={() => { localStorage.setItem('muse_mood',''); alert('Use clicked (demo)'); }} />
          ))}
        </div>
      </section>

      {/* Feedback */}
      <section className="max-w-6xl mx-auto px-6 py-6">
        <h2 className="text-2xl font-semibold mb-4">What people say</h2>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {FEEDBACKS.map((f, i) => <FeedbackCard key={i} quote={f.quote} user={f.user} img={f.img} />)}
        </div>
      </section>
    </div>
  );
}
