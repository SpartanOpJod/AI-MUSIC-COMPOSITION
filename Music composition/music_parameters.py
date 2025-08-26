# music_parameters.py

def map_to_music(mood: str, sentiment: str, energy: int):
    # Base tempo for moods
    tempo_map = {
        "happy": 120,
        "sad": 70,
        "calm": 85,
        "energetic": 140,
        "mysterious": 90,
        "romantic": 100,
    }

    # Instruments per mood
    instruments_map = {
        "happy": ["piano", "guitar", "drums"],
        "sad": ["piano", "strings", "cello"],
        "calm": ["flute", "harp", "synth"],
        "energetic": ["guitar", "drums", "bass"],
        "mysterious": ["synth", "violin", "cello"],
        "romantic": ["piano", "violin", "flute"],
    }

    # Key based on sentiment
    key = "major" if sentiment == "positive" else "minor"

    # Adjust tempo by energy
    base_tempo = tempo_map.get(mood, 100)
    tempo = base_tempo + (energy - 5) * 5  # adjust ±25 BPM

    return {
        "tempo": tempo,
        "key": key,
        "instruments": instruments_map.get(mood, ["piano"]),
    }
