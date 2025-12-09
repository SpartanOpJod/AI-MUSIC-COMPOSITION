def map_to_music(mood, sentiment, energy):
    
    mood_to_tempo = {
        "happy": 120,
        "sad": 70,
        "calm": 85,
        "energetic": 140,
        "mysterious": 100,
        "romantic": 95
    }
    base_tempo = mood_to_tempo.get(mood, 100)
    tempo = base_tempo + (energy - 5) * 2

    
    key = "major" if "positive" in sentiment else "minor"

    
    mood_instruments = {
        "happy": ["piano", "guitar", "drums"],
        "sad": ["piano", "strings", "cello"],
        "calm": ["flute", "piano", "violin"],
        "energetic": ["guitar", "drums", "synth"],
        "mysterious": ["violin", "cello", "synth"],
        "romantic": ["piano", "violin", "saxophone"]
    }
    instruments = mood_instruments.get(mood, ["piano"])

    return {
        "tempo": tempo,
        "key": key,
        "mood": mood,
        "energy": energy,
        "instruments": instruments
    }
