# music_generator.py
import requests
import base64
import os
import tempfile
import time
import random

# Your Colab Gradio share URL
COLAB_URL = os.environ.get("COLAB_URL", "https://7ed2b9011c9364a713.gradio.live")

def query_musicgen_colab(prompt: str, duration: int = 10, colab_url: str = None, timeout: int = 600):
    url = colab_url or COLAB_URL
    if not url:
        raise Exception("COLAB_URL not set. Set COLAB_URL env var or pass colab_url.")
    predict_url = url.rstrip("/") + "/run/predict"
    payload = {"data": [prompt, int(duration)]}
    headers = {"Content-Type": "application/json"}
    
    resp = requests.post(predict_url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json().get("data")
    if not data:
        raise Exception("Empty response data from Colab Gradio.")
    
    first = data[0]
    if isinstance(first, str) and first.startswith("data:"):
        _, b64 = first.split(",", 1)
        return base64.b64decode(b64)
    
    raise Exception("Unexpected response format from Gradio/Colab: " + str(first))

def generate_dummy_wav_bytes(prompt: str, duration: int = 10, sr: int = 32000):
    import numpy as np, io, wave
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Use timestamp + random for truly unique frequencies
    freq = 220.0 + ((int(time.time() * 1000000) + random.randint(0, 10000)) % 200)
    audio = 0.3 * np.sin(2 * np.pi * freq * t)
    audio += 0.12 * np.sin(2 * np.pi * (freq*2) * t)
    for i in range(0, len(t), int(sr * (60/120))):
        hi = np.random.normal(0, 0.05, min(2000, len(t)-i))
        audio[i:i+len(hi)] += hi
    audio = audio / (np.max(np.abs(audio)) + 1e-9)
    audio_int16 = (audio * 32767).astype('int16')
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
    return buf.getvalue()

def query_musicgen(prompt: str, duration: int = 10, use_colab: bool = True, colab_url: str = None):
    if use_colab:
        try:
            return query_musicgen_colab(prompt, duration=duration, colab_url=colab_url)
        except Exception as e:
            print("Colab call failed — using dummy generator:", e)
            return generate_dummy_wav_bytes(prompt, duration)
    else:
        return generate_dummy_wav_bytes(prompt, duration)
