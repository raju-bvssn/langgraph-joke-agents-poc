"""
Evaluator utilities for formatting and processing critic feedback.
"""
from typing import Dict, Any, List


def format_feedback_for_display(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format critic feedback for UI display.
    
    Args:
        feedback: Raw feedback dictionary from critic
    
    Returns:
        Formatted feedback dictionary with additional display fields
    """
    formatted = feedback.copy()
    
    # Add score category
    score = feedback.get("laughability_score", 0)
    if score >= 80:
        formatted["score_category"] = "Excellent"
        formatted["score_emoji"] = "🔥"
    elif score >= 60:
        formatted["score_category"] = "Good"
        formatted["score_emoji"] = "👍"
    elif score >= 40:
        formatted["score_category"] = "Fair"
        formatted["score_emoji"] = "😐"
    else:
        formatted["score_category"] = "Needs Work"
        formatted["score_emoji"] = "😬"
    
    return formatted


def calculate_improvement(old_score: int, new_score: int) -> Dict[str, Any]:
    """
    Calculate improvement metrics between two scores.
    
    Args:
        old_score: Previous laughability score
        new_score: New laughability score
    
    Returns:
        Dictionary with improvement metrics
    """
    delta = new_score - old_score
    percentage_change = (delta / old_score * 100) if old_score > 0 else 0
    
    return {
        "delta": delta,
        "percentage_change": percentage_change,
        "improved": delta > 0,
        "declined": delta < 0,
        "unchanged": delta == 0
    }


def extract_key_weaknesses(feedback: Dict[str, Any], max_items: int = 3) -> List[str]:
    """
    Extract the most important weaknesses from feedback.
    
    Args:
        feedback: Feedback dictionary
        max_items: Maximum number of weaknesses to return
    
    Returns:
        List of key weakness strings
    """
    weaknesses = feedback.get("weaknesses", [])
    return weaknesses[:max_items]


def extract_key_suggestions(feedback: Dict[str, Any], max_items: int = 3) -> List[str]:
    """
    Extract the most important suggestions from feedback.
    
    Args:
        feedback: Feedback dictionary
        max_items: Maximum number of suggestions to return
    
    Returns:
        List of key suggestion strings
    """
    suggestions = feedback.get("suggestions", [])
    return suggestions[:max_items]


def generate_summary(feedback: Dict[str, Any]) -> str:
    """
    Generate a one-line summary of the feedback.
    
    Args:
        feedback: Feedback dictionary
    
    Returns:
        Summary string
    """
    score = feedback.get("laughability_score", 0)
    age = feedback.get("age_appropriateness", "Unknown")
    verdict = feedback.get("overall_verdict", "")
    
    # Truncate verdict if too long
    if len(verdict) > 100:
        verdict = verdict[:97] + "..."
    
    return f"Score: {score}/100 | Age: {age} | {verdict}"


def is_acceptable(feedback: Dict[str, Any], threshold: int = 60) -> bool:
    """
    Determine if a joke meets the acceptability threshold.
    
    Args:
        feedback: Feedback dictionary
        threshold: Minimum acceptable score
    
    Returns:
        True if joke meets threshold
    """
    score = feedback.get("laughability_score", 0)
    return score >= threshold

