import re
from collections import Counter

def normalize_street(text):
    """The Cleaning Logic"""
    return re.sub(r'\d+', '', text).strip()

def calculate_best_spot(matches):
    """The Math Logic"""
    if not matches:
        return None, 0, 0
    counts = Counter(matches)
    best_spot, occurrences = counts.most_common(1)[0]
    confidence = (occurrences / len(matches)) * 100
    return f"Prediction: {best_spot} ({confidence:.0f}% confidence based on {len(matches)} historical records)."