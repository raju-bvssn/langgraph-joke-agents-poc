"""
Formatting utilities for displaying content in the UI.
"""
from typing import List, Tuple
import difflib


def get_text_diff(old_text: str, new_text: str) -> List[Tuple[str, str]]:
    """
    Generate a word-level diff between two texts.
    
    Args:
        old_text: Original text
        new_text: Revised text
    
    Returns:
        List of (status, word) tuples where status is '', '-', or '+'
    """
    old_words = old_text.split()
    new_words = new_text.split()
    
    diff = []
    matcher = difflib.SequenceMatcher(None, old_words, new_words)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            diff.extend([('', word) for word in old_words[i1:i2]])
        elif tag == 'delete':
            diff.extend([('-', word) for word in old_words[i1:i2]])
        elif tag == 'insert':
            diff.extend([('+', word) for word in new_words[j1:j2]])
        elif tag == 'replace':
            diff.extend([('-', word) for word in old_words[i1:i2]])
            diff.extend([('+', word) for word in new_words[j1:j2]])
    
    return diff


def format_score_badge(score: int, max_score: int = 100) -> str:
    """
    Format a score as a colored badge.
    
    Args:
        score: The score value
        max_score: Maximum possible score
    
    Returns:
        HTML string for the badge
    """
    percentage = (score / max_score) * 100
    
    if percentage >= 80:
        color = "#2ECC71"  # Green
        emoji = "🔥"
    elif percentage >= 60:
        color = "#F39C12"  # Orange
        emoji = "👍"
    elif percentage >= 40:
        color = "#E67E22"  # Dark orange
        emoji = "😐"
    else:
        color = "#E74C3C"  # Red
        emoji = "😬"
    
    return f'<span style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{emoji} {score}/{max_score}</span>'


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
