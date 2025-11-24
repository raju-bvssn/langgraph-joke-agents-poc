"""
LangGraph Workflow - Orchestrates Performer and Critic agents.
Demonstrates state passing and multi-agent collaboration.
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.language_models.chat_models import BaseChatModel

from app.agents.performer import PerformerAgent
from app.agents.critic import CriticAgent


# Define the shared state structure
class JokeWorkflowState(TypedDict, total=False):
    """
    Shared state passed between agents in the workflow.
    
    Fields:
        prompt: User's joke topic/theme
        joke: Generated joke from Performer
        feedback: Structured evaluation from Critic
        performer_completed: Flag indicating Performer finished
        critic_completed: Flag indicating Critic finished
    """
    prompt: str
    joke: str
    feedback: dict
    performer_completed: bool
    critic_completed: bool


class JokeWorkflow:
    """
    Multi-agent workflow orchestrating joke generation and evaluation.
    
    Flow:
        1. START → Performer (generates joke)
        2. Performer → Critic (evaluates joke)
        3. Critic → END (returns final state)
    """
    
    def __init__(self, performer_llm: BaseChatModel, critic_llm: BaseChatModel):
        """
        Initialize the workflow with configured LLMs.
        
        Args:
            performer_llm: LLM for creative joke generation
            critic_llm: LLM for analytical joke evaluation
        """
        self.performer_agent = PerformerAgent(performer_llm)
        self.critic_agent = CriticAgent(critic_llm)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph ready for execution.
        """
        # Create the state graph
        workflow = StateGraph(JokeWorkflowState)
        
        # Add agent nodes
        workflow.add_node("performer", self.performer_agent)
        workflow.add_node("critic", self.critic_agent)
        
        # Define the flow
        workflow.set_entry_point("performer")
        workflow.add_edge("performer", "critic")
        workflow.add_edge("critic", END)
        
        # Compile the graph
        return workflow.compile()
    
    def run(self, prompt: str) -> JokeWorkflowState:
        """
        Execute the complete workflow.
        
        Args:
            prompt: User's joke topic or theme
            
        Returns:
            Final state containing joke and feedback
        """
        initial_state: JokeWorkflowState = {
            "prompt": prompt,
            "joke": "",
            "feedback": {},
            "performer_completed": False,
            "critic_completed": False
        }
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        return final_state
    
    async def arun(self, prompt: str) -> JokeWorkflowState:
        """
        Execute the workflow asynchronously.
        
        Args:
            prompt: User's joke topic or theme
            
        Returns:
            Final state containing joke and feedback
        """
        initial_state: JokeWorkflowState = {
            "prompt": prompt,
            "joke": "",
            "feedback": {},
            "performer_completed": False,
            "critic_completed": False
        }
        
        # Run the workflow asynchronously
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state
    
    def revise_joke(self, joke: str, feedback: dict) -> str:
        """
        Revise an existing joke based on critic's feedback.
        
        This is used during iterative refinement when the user accepts
        the evaluation and wants to improve the joke.
        
        Args:
            joke: The original joke to revise
            feedback: Structured feedback from the critic
            
        Returns:
            Revised joke as a string
        """
        return self.performer_agent.revise_joke(joke, feedback)
    
    def evaluate_joke(self, joke: str) -> dict:
        """
        Evaluate a joke using the critic agent.
        
        This is used after revising a joke to get fresh feedback.
        
        Args:
            joke: The joke to evaluate
            
        Returns:
            Structured feedback as a dictionary
        """
        feedback = self.critic_agent.evaluate_joke(joke)
        return feedback.model_dump()
    
    def reevaluate_joke(self, joke: str) -> dict:
        """
        Re-evaluate the same joke to produce refined or clearer feedback.
        
        This is used during iterative refinement when the user rejects
        the evaluation and wants a fresh perspective.
        
        Args:
            joke: The joke to re-evaluate
            
        Returns:
            New structured feedback as a dictionary
        """
        feedback = self.critic_agent.reevaluate_joke(joke)
        return feedback.model_dump()
    
    def get_graph_visualization(self) -> str:
        """
        Get a text representation of the workflow graph.
        
        Returns:
            Graph structure as string
        """
        try:
            # Try to get mermaid diagram
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            # Fallback to simple text representation
            return """
            START
              ↓
            PERFORMER (Generate Joke)
              ↓
            CRITIC (Evaluate Joke)
              ↓
            END
            
            Iterative Refinement:
            - Revise: PERFORMER revises → CRITIC evaluates
            - Re-evaluate: CRITIC provides fresh feedback
            """

