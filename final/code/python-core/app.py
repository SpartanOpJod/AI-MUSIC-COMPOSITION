import streamlit as st
import numpy as np
import random
from music_generator import query_musicgen
from mood_analyzer import MoodAnalyzer
from audio_processor import AudioProcessor
from pydub import AudioSegment
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="🎵 AI Music Composer",
    page_icon="🎼",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center;color:#6C63FF;'>🎼AI Music Composer</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

@st.cache_resource
def load_mood_analyzer():
    return MoodAnalyzer()

mood_analyzer = load_mood_analyzer()

st.sidebar.header("🎶 Music Settings")
colab_url = st.sidebar.text_input(
    "Colab Gradio URL",
    value="https://huggingface.co/spaces/SpartanOp/AI_Music_Generator"
)
use_colab = st.sidebar.checkbox("Use Colab MusicGen", value=True)
prompt = st.sidebar.text_area(
    "Describe the music",
    "Energetic upbeat electronic music"
)
duration = st.sidebar.slider(
    "Duration (seconds)", min_value=10, max_value=30, value=12
)
tempo = st.sidebar.slider(
    "Tempo (BPM)", min_value=60, max_value=180, value=120
)
instruments = st.sidebar.text_input("Instruments", value="synth + drums")

if st.button("🎶 Generate Music"):
    st.info("Generating music... please wait")

    try:
        seed = (hash(prompt) + random.randint(0, 100000)) % (2**32)
        np.random.seed(seed)

        analysis = mood_analyzer.analyze(prompt)
        detected_mood = analysis["mood"]
        energy = analysis["energy"]

        audio_bytes = query_musicgen(
            prompt=prompt,
            duration=duration,
            mood=detected_mood,
            energy=energy,
            use_colab=use_colab,
            colab_url=colab_url.strip()
        )

        processor = AudioProcessor()
        result = processor.process_audio_bytes(
            audio_bytes,
            params={
                "mood": detected_mood,
                "tempo": tempo,
                "instruments": instruments,
                "duration": duration
            },
            output_format="mp3"
        )
        audio_file = result["audio_file"]

        st.success("✅ Music Generated!")
        col1, col2 = st.columns([3, 1])

        with col1:
            st.audio(audio_file, format="audio/mp3")
            st.download_button(
                "⬇️ Download MP3",
                data=open(audio_file, "rb").read(),
                file_name="music.mp3",
                mime="audio/mp3"
            )

            audio_segment = AudioSegment.from_file(audio_file)
            samples = np.array(audio_segment.get_array_of_samples())

            plt.figure(figsize=(12, 2))
            sns.set_style("darkgrid")
            plt.plot(samples)
            plt.title("🎼 Waveform Preview")
            plt.xlabel("Sample")
            plt.ylabel("Amplitude")
            st.pyplot(plt)
            plt.close()

        with col2:
            st.markdown("### 🎵 Music Parameters")
            st.markdown(f"- **Mood:** {detected_mood}")
            st.markdown(f"- **Energy:** {energy}")
            st.markdown(f"- **Duration:** {duration} sec")
            st.markdown(f"- **Tempo:** {tempo} BPM")
            st.markdown(f"- **Instruments:** {instruments}")
            st.markdown(f"- **File Size:** {result['file_size_mb']} MB")

    except Exception as e:
        st.error(f"❌ Music generation failed: {e}")
