import math

def analyze_whisper_result(whisper_result: dict):
    """
    Analyzes the result from Whisper to calculate WPM and silence ratio.
    This method avoids reloading the audio file and is much more efficient.

    Note: For Korean text, WPM is calculated based on word count (어절),
    which results in lower numbers compared to English.
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

    # 2. Calculate Word Count (Korean: 어절 단위)
    num_words = len(full_text.split())

    # 3. Calculate WPM (Words Per Minute)
    minutes = total_duration / 60
    wpm = num_words / minutes if minutes > 0 else 0.0

    # 4. Calculate Silence Ratio (improved)
    # Calculate gaps between segments as silence
    silence_duration = 0.0

    for i in range(len(segments) - 1):
        gap = segments[i + 1]["start"] - segments[i]["end"]
        if gap > 0:
            silence_duration += gap

    # Also consider silence at the beginning
    if segments[0]["start"] > 0:
        silence_duration += segments[0]["start"]

    # Calculate silence ratio
    # Note: If there's only 1 segment with no gaps, silence_ratio will be minimal
    # We can also use no_speech_prob as an indicator
    silence_ratio = (silence_duration / total_duration) * 100 if total_duration > 0 else 0.0

    # If silence ratio is very low but no_speech_prob is high, adjust
    # This handles cases where Whisper detects hesitation/pauses within a segment
    if len(segments) > 0:
        avg_no_speech_prob = sum(seg.get("no_speech_prob", 0.0) for seg in segments) / len(segments)
        # If average no_speech_prob is high (>0.2), add it as additional silence indicator
        if avg_no_speech_prob > 0.2 and silence_ratio < 5.0:
            # Estimate additional silence based on no_speech_prob
            silence_ratio += avg_no_speech_prob * 10  # Scale factor for adjustment

    return wpm, silence_ratio
