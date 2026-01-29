import io
import wave
import numpy as np
import requests
import base64
import os

COLAB_URL = os.environ.get(
    "COLAB_URL",
    "https://huggingface.co/spaces/SpartanOp/AI_Music_Generator"
)

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
    audio = audio / (np.max(np.abs(audio)) + 1e-9)

    audio_int16 = (audio * 32767).astype("int16")

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

    return buf.getvalue()


def query_musicgen_colab(prompt, duration=10, timeout=120):
    url = COLAB_URL.rstrip("/")

    response = requests.post(
        f"{url}/gradio_api/call/generate_music",
        json={"data": [prompt, duration]},
        timeout=timeout,
    )
    response.raise_for_status()

    event_id = response.json()["event_id"]

    stream = requests.get(
        f"{url}/gradio_api/call/generate_music/{event_id}",
        stream=True,
        timeout=timeout,
    )

    for line in stream.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if '"data"' in decoded:
                b64 = decoded.split('"')[-2]
                if "," in b64:
                    b64 = b64.split(",", 1)[1]
                return base64.b64decode(b64)

    raise Exception("No audio returned from HF Space")


def query_musicgen(prompt, duration, mood, energy, use_colab=True):
    if use_colab:
        return query_musicgen_colab(prompt, duration)
    return generate_dummy_wav_bytes(prompt, duration, mood=mood, energy=energy)
