import re
from typing import Dict, List, Tuple, Any

def find_indices(text: str, error_text: str) -> Tuple[int, int]:
    start = text.find(error_text)
    if start == -1:
        pattern = re.compile(re.escape(error_text), re.IGNORECASE)
        match = pattern.search(text)
        if match:
            start = match.start()
            return start, start + len(error_text)
        return -1, -1
    
    return start, start + len(error_text)

def format_error(text: str, start: int, end: int, correction: str) -> Dict[str, Any]:
    return {
        "start": start,
        "end": end,
        "wrong_version": text[start:end],
        "correct_version": correction
    }

def merge_overlapping_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not errors:
        return []
    
    sorted_errors = sorted(errors, key=lambda x: x["start"])
    merged = [sorted_errors[0]]
    
    for current in sorted_errors[1:]:
        previous = merged[-1]
        
        if current["start"] <= previous["end"]:
            merged[-1] = {
                "start": previous["start"],
                "end": max(previous["end"], current["end"]),
                "wrong_version": previous["wrong_version"],
                "correct_version": previous["correct_version"]
            }
        else:
            merged.append(current)
    
    return merged

def calculate_coherence_score(paragraph: str) -> float:
    # Simple coherence metrics:
    # 1. Sentence length variation (too much variation might indicate incoherence)
    # 2. Presence of transition words
    # 3. Repetition of words or phrases
    
    # This is a simplified implementation
    sentences = re.split(r'[.!?]+', paragraph)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0.0
    
    # Check for transition words
    transition_words = [
        "however", "therefore", "furthermore", "moreover", "in addition",
        "consequently", "as a result", "for instance", "for example",
        "in conclusion", "finally", "thus", "hence", "accordingly"
    ]
    
    transition_count = sum(1 for word in transition_words if word.lower() in paragraph.lower())
    
    # Check for sentence length variation
    avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
    length_variation = sum(abs(len(s.split()) - avg_length) for s in sentences) / len(sentences)
    
    # Normalize the variation (lower is better)
    normalized_variation = max(0, 1 - (length_variation / avg_length))
    
    # Calculate transition word density
    transition_density = min(1.0, transition_count / max(1, len(sentences)))
    
    # Simple coherence score (can be improved with more sophisticated NLP)
    coherence_score = (normalized_variation * 0.7) + (transition_density * 0.3)
    
    return min(1.0, max(0.0, coherence_score))
