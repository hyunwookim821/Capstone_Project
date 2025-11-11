import librosa
import numpy as np
import soundfile as sf
from typing import Tuple

def analyze_speech_audio(audio_path: str, transcript: str) -> Tuple[float, float]:
    """
    Analyzes an audio file to calculate speech rate and silence ratio.

    Args:
        audio_path: Path to the audio file.
        transcript: The transcribed text of the audio.

    Returns:
        A tuple containing:
        - speech_rate (words per minute)
        - silence_ratio (percentage of silence in the audio)
    """
    try:
        # Load audio file
        y, sr = sf.read(audio_path)
        # Ensure it's mono
        if y.ndim > 1:
            y = y.mean(axis=1)
    except Exception as e:
        print(f"Could not read audio file {audio_path}: {e}")
        return 0.0, 0.0

    # --- 1. Calculate Speech Rate (Words Per Minute) ---
    duration_seconds = librosa.get_duration(y=y, sr=sr)
    word_count = len(transcript.split())
    
    speech_rate = 0.0
    if duration_seconds > 0:
        minutes = duration_seconds / 60
        speech_rate = word_count / minutes if minutes > 0 else 0

    # --- 2. Calculate Silence Ratio ---
    # Split audio into non-silent parts
    non_silent_intervals = librosa.effects.split(y, top_db=30) # top_db can be adjusted
    
    silent_duration = 0.0
    if len(non_silent_intervals) > 0:
        non_silent_duration = sum(librosa.samples_to_time(interval[1] - interval[0], sr=sr) for interval in non_silent_intervals)
        silent_duration = duration_seconds - non_silent_duration
    else:
        # If no non-silent parts are found, the whole audio is considered silent
        silent_duration = duration_seconds

    silence_ratio = 0.0
    if duration_seconds > 0:
        silence_ratio = (silent_duration / duration_seconds) * 100

    return speech_rate, silence_ratio
