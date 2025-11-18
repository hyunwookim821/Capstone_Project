import math

def analyze_whisper_result(whisper_result: dict):
    """
    Analyzes the result from Whisper to calculate WPM and silence ratio.
    This method avoids reloading the audio file and is much more efficient.
    """
    if not whisper_result or not whisper_result.get("segments"):
        return 0.0, 0.0

    segments = whisper_result["segments"]
    full_text = whisper_result.get("text", "").strip()

    if not full_text:
        return 0.0, 0.0

    # 1. Calculate total duration from the last segment's end time
    total_duration = segments[-1]["end"]
    if total_duration == 0:
        return 0.0, 0.0

    # 2. Calculate Word Count
    num_words = len(full_text.split())

    # 3. Calculate WPM (Words Per Minute)
    minutes = total_duration / 60
    wpm = num_words / minutes if minutes > 0 else 0.0

    # 4. Calculate Silence Ratio
    # Sum the duration of actual speech segments
    speech_duration = sum(seg["end"] - seg["start"] for seg in segments)
    
    # Silence duration is the total time minus the time spent speaking
    silence_duration = total_duration - speech_duration
    
    silence_ratio = (silence_duration / total_duration) * 100 if total_duration > 0 else 0.0

    return wpm, silence_ratio
