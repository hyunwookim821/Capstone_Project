import numpy as np
from typing import List, Dict, Any

def analyze_video_landmarks(landmark_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Analyzes a list of landmark data from video frames to calculate stability metrics.

    Args:
        landmark_data: A list of dictionaries, where each dictionary represents
                       the detected landmarks for a single frame.
                       Expected format: [{'face': [...], 'pose': [...]}, ...]

    Returns:
        A dictionary containing stability scores for gaze, expression, and posture.
        Scores are typically standard deviations, where lower is more stable.
    """
    if not landmark_data:
        return {
            "gaze_stability": 0.0,
            "expression_stability": 0.0,
            "posture_stability": 0.0,
        }

    # --- Gaze Stability (approximated by head pose stability) ---
    # We use the nose tip as a proxy for head center position.
    nose_positions = [frame['face'][1]['x'] for frame in landmark_data if 'face' in frame and len(frame['face']) > 1]
    gaze_stability = np.std(nose_positions) if nose_positions else 0.0

    # --- Expression Stability (approximated by mouth corner movement) ---
    # We track the standard deviation of the distance between mouth corners.
    left_mouth_corner_idx = 61
    right_mouth_corner_idx = 291
    mouth_widths = []
    for frame in landmark_data:
        if 'face' in frame and len(frame['face']) > right_mouth_corner_idx:
            left_corner = frame['face'][left_mouth_corner_idx]
            right_corner = frame['face'][right_mouth_corner_idx]
            width = np.sqrt((left_corner['x'] - right_corner['x'])**2 + (left_corner['y'] - right_corner['y'])**2)
            mouth_widths.append(width)
    expression_stability = np.std(mouth_widths) if mouth_widths else 0.0

    # --- Posture Stability (approximated by shoulder alignment) ---
    # We track the standard deviation of the vertical distance between shoulders.
    left_shoulder_idx = 11
    right_shoulder_idx = 12
    shoulder_height_diffs = []
    for frame in landmark_data:
        if 'pose' in frame and len(frame['pose']) > right_shoulder_idx:
            left_shoulder = frame['pose'][left_shoulder_idx]
            right_shoulder = frame['pose'][right_shoulder_idx]
            height_diff = abs(left_shoulder['y'] - right_shoulder['y'])
            shoulder_height_diffs.append(height_diff)
    posture_stability = np.std(shoulder_height_diffs) if shoulder_height_diffs else 0.0

    return {
        "gaze_stability": float(gaze_stability),
        "expression_stability": float(expression_stability),
        "posture_stability": float(posture_stability),
    }
