# music_generator.py
import io
import wave
import numpy as np


def generate_dummy_wav_bytes(
    prompt: str,
    duration: int = 10,
    sr: int = 32000,
    mood: str = "calm",
    energy: int = 5,
):
    mood_freq_map = {
        "happy": 440,
        "sad": 180,
        "calm": 220,
        "energetic": 660,
        "mysterious": 260,
        "romantic": 300,
    }

    base_freq = mood_freq_map.get(mood, 220)
    base_freq += (energy - 5) * 15

    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    audio = 0.35 * np.sin(2 * np.pi * base_freq * t)

    if energy > 6:
        audio += 0.2 * np.sin(2 * np.pi * base_freq * 2 * t)
    else:
        audio += 0.1 * np.sin(2 * np.pi * base_freq * 0.5 * t)

    audio = audio / (np.max(np.abs(audio)) + 1e-9)
    audio_int16 = (audio * 32767).astype("int16")

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

    return buf.getvalue()


def query_musicgen(
    prompt,
    duration=10,
    mood="calm",
    energy=5,
    use_colab=True,
    colab_url=None,
):
    # HF Space is UI-only; generate locally using AI-conditioned parameters
    return generate_dummy_wav_bytes(
        prompt,
        duration,
        mood=mood,
        energy=energy,
    )
