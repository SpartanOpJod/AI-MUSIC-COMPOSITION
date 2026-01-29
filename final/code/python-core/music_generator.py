from gradio_client import Client
import os

COLAB_URL = os.environ.get(
    "COLAB_URL",
    "https://spartanop-ai-music-generator.hf.space"
)

def query_musicgen(prompt, duration, mood=None, energy=None, use_colab=True):
    client = Client(COLAB_URL)

    audio_path, mood = client.predict(
        prompt,
        duration,
        api_name="/predict"
    )

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    return audio_bytes
