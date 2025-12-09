import os
import io
import tempfile
from pydub import AudioSegment

class AudioProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def process_audio_bytes(self, audio_bytes, params=None, output_format="mp3"):
        """
        Accept audio bytes (MP3/WAV/etc.), convert internally, return MP3/WAV.
        """
        params = params or {}
        duration = params.get("duration", 10)
        filename = f"music_{int(duration)}s"

        # Load bytes into AudioSegment (auto-detect format)
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Optional: ensure minimum duration
        if len(audio) < duration * 1000:
            silence = AudioSegment.silent(duration=(duration*1000 - len(audio)))
            audio += silence

        # Save WAV first
        wav_path = os.path.join(self.temp_dir, filename + ".wav")
        audio.export(wav_path, format="wav")

        # Convert to MP3 if requested
        final_path = wav_path
        if output_format.lower() in ["mp3", "mp3file"]:
            final_path = os.path.join(self.temp_dir, filename + ".mp3")
            audio.export(final_path, format="mp3", bitrate="192k")

        return {
            "audio_file": final_path,
            "processing_successful": True,
            "file_size_mb": round(os.path.getsize(final_path) / (1024*1024), 3)
        }
