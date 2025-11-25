"""
Factory for creating agent instances with configured LLMs.
"""
from app.agents.performer import PerformerAgent
from app.agents.critic import CriticAgent
from app.llm.factory import create_performer_llm, create_critic_llm


class AgentFactory:
    """Factory for creating configured agent instances."""
    
    @staticmethod
    def create_performer(provider: str, model: str = None) -> PerformerAgent:
        """
        Create a Performer agent with the specified LLM configuration.
        
        Args:
            provider: LLM provider name
            model: Model identifier (uses default if None)
        
        Returns:
            Configured PerformerAgent instance
        """
        llm = create_performer_llm(provider, model)
        return PerformerAgent(llm)
    
    @staticmethod
    def create_critic(provider: str, model: str = None) -> CriticAgent:
        """
        Create a Critic agent with the specified LLM configuration.
        
        Args:
            provider: LLM provider name
            model: Model identifier (uses default if None)
        
        Returns:
            Configured CriticAgent instance
        """
        llm = create_critic_llm(provider, model)
        return CriticAgent(llm)
    
    @staticmethod
    def create_agent_pair(
        performer_provider: str,
        performer_model: str = None,
        critic_provider: str = None,
        critic_model: str = None
    ) -> tuple[PerformerAgent, CriticAgent]:
        """
        Create a matched pair of Performer and Critic agents.
        
        Args:
            performer_provider: Provider for Performer agent
            performer_model: Model for Performer agent
            critic_provider: Provider for Critic agent (uses performer_provider if None)
            critic_model: Model for Critic agent
        
        Returns:
            Tuple of (PerformerAgent, CriticAgent)
        """
        if critic_provider is None:
            critic_provider = performer_provider
        
        performer = AgentFactory.create_performer(performer_provider, performer_model)
        critic = AgentFactory.create_critic(critic_provider, critic_model)
        
        return performer, critic

