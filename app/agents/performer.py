"""
Performer Agent - Generates original jokes based on prompts.
Uses high temperature for creative output.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Dict, Any


class PerformerAgent:
    """
    The Performer Agent generates jokes based on user prompts.
    It focuses on creativity, originality, and entertainment value.
    """
    
    SYSTEM_PROMPT = """You are a creative comedian and joke writer.

Your task is to generate ORIGINAL, FUNNY jokes based on the given theme or prompt.

Guidelines:
- Be creative and witty
- Keep jokes concise (2-4 sentences max)
- Make them memorable and punchy
- Aim for surprise and clever wordplay
- Consider different joke formats (puns, one-liners, setup-punchline, etc.)
- Stay tasteful and avoid offensive content

Generate ONE complete joke that will make people laugh."""

    def __init__(self, llm: BaseChatModel):
        """
        Initialize the Performer agent.
        
        Args:
            llm: Language model configured for creative generation.
        """
        self.llm = llm
    
    def generate_joke(self, prompt: str) -> str:
        """
        Generate a joke based on the given prompt.
        
        Args:
            prompt: The theme or topic for the joke.
            
        Returns:
            Generated joke as a string.
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Generate a joke about: {prompt}")
        ]
        
        response = self.llm.invoke(messages)
        joke = response.content.strip()
        
        return joke
    
    def revise_joke(self, joke: str, feedback: Dict[str, Any]) -> str:
        """
        Revise an existing joke based on critic's feedback.
        
        Args:
            joke: The original joke to revise.
            feedback: Structured feedback from the critic containing weaknesses and suggestions.
            
        Returns:
            Revised joke as a string.
        """
        # Build context from feedback
        weaknesses = feedback.get('weaknesses', [])
        suggestions = feedback.get('suggestions', [])
        score = feedback.get('laughability_score', 0)
        
        revision_context = f"""Original joke received a score of {score}/100.

Weaknesses identified:
{chr(10).join(f'- {w}' for w in weaknesses)}

Suggestions for improvement:
{chr(10).join(f'- {s}' for s in suggestions)}"""
        
        revision_prompt = f"""You are revising a joke to make it better.

{revision_context}

Original joke:
"{joke}"

Your task: Rewrite this joke to address the weaknesses and incorporate the suggestions.
- Keep the core concept but improve the delivery
- Make it funnier and more polished
- Fix any issues mentioned in the feedback
- Keep it concise (2-4 sentences max)

Generate the REVISED joke:"""
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=revision_prompt)
        ]
        
        response = self.llm.invoke(messages)
        revised_joke = response.content.strip()
        
        return revised_joke
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Performer agent within a LangGraph workflow.
        
        Args:
            state: Current workflow state containing 'prompt'.
            
        Returns:
            Updated state with 'joke' field.
        """
        prompt = state.get("prompt", "")
        
        if not prompt:
            raise ValueError("No prompt provided for joke generation")
        
        joke = self.generate_joke(prompt)
        
        return {
            "joke": joke,
            "performer_completed": True
        }

