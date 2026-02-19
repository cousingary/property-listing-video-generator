# tts_engine.py
from google.cloud import texttospeech
import os

def generate_tts(text, voice, speed_factor=1.0, output_path="voice.mp3", **kwargs):
    # --- ADD THIS LOGIC HERE ---
    # Thai script needs explicit dots to avoid "Sentence too long" errors.
    # We replace every space or double-space with a period.
    if "th-TH" in voice:
        text = text.replace("  ", ". ").replace(" ", ". ")
    # ---------------------------

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    # In 2026, Chirp voices use 'model_name' inside VoiceSelectionParams
    # But to prevent crashes, we'll build the dictionary manually
    voice_config = {
        "language_code": "th-TH",
        "name": voice
    }

    # If the voice is a Chirp HD voice, we add the model_name field
    if "Chirp" in voice or "HD" in voice:
        # 'google-speech-model' is the required model for Chirp HD
        voice_config["model_name"] = "google-speech-model"

    voice_params = texttospeech.VoiceSelectionParams(voice_config)

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speed_factor
    )

    # Final Request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice_params,
        audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    return output_path