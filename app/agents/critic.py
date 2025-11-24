"""
Critic Agent - Evaluates jokes with structured metrics and feedback.
Uses lower temperature for consistent, analytical evaluation.
"""
from typing import Dict, Any, List, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class JokeFeedback(BaseModel):
    """Structured feedback from the Critic agent."""
    
    laughability_score: int = Field(
        description="How funny is this joke? Score from 0-100.",
        ge=0,
        le=100
    )
    age_appropriateness: Literal["Child", "Teen", "Adult"] = Field(
        description="Target audience based on content maturity"
    )
    strengths: List[str] = Field(
        description="What works well in this joke (2-3 points)",
        min_length=1
    )
    weaknesses: List[str] = Field(
        description="What could be improved (2-3 points)",
        min_length=1
    )
    suggestions: List[str] = Field(
        description="Specific actionable recommendations for improvement",
        min_length=1
    )
    overall_verdict: str = Field(
        description="One sentence summary of the joke's quality"
    )


class CriticAgent:
    """
    The Critic Agent evaluates jokes using structured metrics.
    It provides constructive feedback to help improve joke quality.
    """
    
    SYSTEM_PROMPT = """You are an expert comedy critic and writing coach.

Your task is to evaluate jokes objectively and provide constructive feedback.

Evaluate the joke based on:
1. **Laughability Score (0-100)**: How funny is it? Does it land?
2. **Age Appropriateness**: Child / Teen / Adult based on content
3. **Strengths**: What works well (humor technique, timing, wordplay, etc.)
4. **Weaknesses**: What falls flat or could be improved
5. **Suggestions**: Specific, actionable recommendations

Be honest but constructive. Your goal is to help improve comedy writing.

You MUST respond with valid JSON matching this exact structure:
{
    "laughability_score": <number 0-100>,
    "age_appropriateness": "<Child|Teen|Adult>",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "overall_verdict": "<one sentence summary>"
}"""

    def __init__(self, llm: BaseChatModel):
        """
        Initialize the Critic agent.
        
        Args:
            llm: Language model configured for analytical evaluation.
        """
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=JokeFeedback)
    
    def evaluate_joke(self, joke: str) -> JokeFeedback:
        """
        Evaluate a joke and provide structured feedback.
        
        Args:
            joke: The joke text to evaluate.
            
        Returns:
            Structured feedback as JokeFeedback object.
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(
                content=f"Evaluate this joke:\n\n\"{joke}\"\n\n"
                        f"Respond with valid JSON only."
            )
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON response
        try:
            feedback_dict = self.parser.parse(response.content)
            feedback = JokeFeedback(**feedback_dict)
        except Exception as e:
            # Fallback if parsing fails
            print(f"Warning: Failed to parse feedback: {e}")
            feedback = JokeFeedback(
                laughability_score=50,
                age_appropriateness="Teen",
                strengths=["Joke was generated"],
                weaknesses=["Could not properly evaluate"],
                suggestions=["Try again with clearer joke structure"],
                overall_verdict="Evaluation incomplete due to parsing error"
            )
        
        return feedback
    
    def reevaluate_joke(self, joke: str) -> JokeFeedback:
        """
        Re-evaluate the same joke to produce refined or clearer feedback.
        
        This method provides a fresh perspective on the same joke, potentially
        catching different aspects or providing more detailed feedback.
        
        Args:
            joke: The joke text to re-evaluate.
            
        Returns:
            New structured feedback as JokeFeedback object.
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT + "\n\nNote: You are providing a fresh, independent evaluation of this joke. Focus on providing clear, actionable feedback."),
            HumanMessage(
                content=f"Provide a fresh evaluation of this joke:\n\n\"{joke}\"\n\n"
                        f"Respond with valid JSON only."
            )
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON response
        try:
            feedback_dict = self.parser.parse(response.content)
            feedback = JokeFeedback(**feedback_dict)
        except Exception as e:
            # Fallback if parsing fails
            print(f"Warning: Failed to parse feedback: {e}")
            feedback = JokeFeedback(
                laughability_score=50,
                age_appropriateness="Teen",
                strengths=["Joke was generated"],
                weaknesses=["Could not properly evaluate"],
                suggestions=["Try again with clearer joke structure"],
                overall_verdict="Re-evaluation incomplete due to parsing error"
            )
        
        return feedback
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Critic agent within a LangGraph workflow.
        
        Args:
            state: Current workflow state containing 'joke'.
            
        Returns:
            Updated state with 'feedback' field.
        """
        joke = state.get("joke", "")
        
        if not joke:
            raise ValueError("No joke provided for evaluation")
        
        feedback = self.evaluate_joke(joke)
        
        return {
            "feedback": feedback.model_dump(),
            "critic_completed": True
        }

