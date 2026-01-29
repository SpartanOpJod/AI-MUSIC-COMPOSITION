from gradio_client import Client
import os

COLAB_URL = os.environ.get(
    "COLAB_URL",
    "https://huggingface.co/spaces/SpartanOp/AI_Music_Generator"
)

client = Client(COLAB_URL)

def query_musicgen(prompt, duration, mood, energy, use_colab=True):
    audio, _ = client.predict(
        prompt,
        duration,
        api_name="/predict"
    )
    return audio
