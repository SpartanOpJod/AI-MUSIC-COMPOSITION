from gradio_client import Client
import os
import base64

COLAB_URL = os.environ.get(
    "COLAB_URL",
    "https://spartanop-ai-music-generator.hf.space"
)

def query_musicgen(prompt, duration, mood=None, energy=None, use_colab=True):
    client = Client(COLAB_URL)

    result = client.predict(
        prompt,
        duration,
        fn_index=0   
    )

    audio = result[0]

    # 🔥 normalize to bytes
    if isinstance(audio, str):
        if "," in audio:
            audio = audio.split(",", 1)[1]
        audio = base64.b64decode(audio)

    return audio
