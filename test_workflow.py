#!/usr/bin/env python3
"""
Simple CLI test script to verify the workflow without Streamlit.

Usage: 
  python test_workflow.py "your joke topic"
  python test_workflow.py "topic" --performer-provider groq --performer-model llama-3.3-70b-versatile
  python test_workflow.py "topic" --critic-provider openai --critic-model gpt-4o-mini
"""
import sys
import argparse
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.llm import get_performer_llm, get_critic_llm
from app.graph.workflow import JokeWorkflow
from app.utils.settings import settings, MODEL_CATALOG
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def main():
    console = Console()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Test the multi-agent joke workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_workflow.py "artificial intelligence"
  python test_workflow.py "cats" --performer-provider groq
  python test_workflow.py "coffee" --performer-provider groq --critic-provider openai
  python test_workflow.py "coding" --performer-model llama-3.1-70b-versatile --critic-model gpt-4o
        """
    )
    parser.add_argument("topic", nargs="?", default="artificial intelligence", help="Joke topic")
    parser.add_argument("--performer-provider", choices=list(MODEL_CATALOG.keys()), help="Performer LLM provider")
    parser.add_argument("--performer-model", help="Performer LLM model")
    parser.add_argument("--critic-provider", choices=list(MODEL_CATALOG.keys()), help="Critic LLM provider")
    parser.add_argument("--critic-model", help="Critic LLM model")
    
    args = parser.parse_args()
    
    # Banner
    console.print(Panel.fit(
        "[bold cyan]🎭 Multi-Agent Joke System - CLI Test[/bold cyan]",
        border_style="cyan"
    ))
    
    # Check configuration
    try:
        # Check if required keys are available for selected providers
        performer_provider = args.performer_provider or settings.llm_provider
        critic_provider = args.critic_provider or settings.llm_provider
        
        if performer_provider == "openai" or critic_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        
        if performer_provider == "groq" or critic_provider == "groq":
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is required when using Groq provider")
                
        console.print(f"✅ Configuration validated\n")
    except ValueError as e:
        console.print(f"[red]❌ Configuration Error:[/red] {e}")
        console.print("\n[yellow]Please set the required API keys in your .env file[/yellow]")
        sys.exit(1)
    
    prompt = args.topic
    if not prompt or prompt == "artificial intelligence":
        console.print(f"[yellow]Using default topic:[/yellow] {prompt}\n")
    
    console.print(f"[bold]Topic:[/bold] {prompt}\n")
    
    # Display LLM configuration
    config_table = Table(show_header=True, box=None)
    config_table.add_column("Agent", style="bold")
    config_table.add_column("Provider")
    config_table.add_column("Model")
    config_table.add_column("Temp")
    
    config_table.add_row(
        "🎭 Performer",
        args.performer_provider or settings.llm_provider,
        args.performer_model or "default",
        "0.9"
    )
    config_table.add_row(
        "🧐 Critic",
        args.critic_provider or settings.llm_provider,
        args.critic_model or "default",
        "0.3"
    )
    
    console.print(config_table)
    console.print()
    
    # Initialize workflow with selected LLMs
    console.print("[dim]Initializing agents...[/dim]")
    performer_llm = get_performer_llm(
        provider=args.performer_provider,
        model=args.performer_model
    )
    critic_llm = get_critic_llm(
        provider=args.critic_provider,
        model=args.critic_model
    )
    workflow = JokeWorkflow(performer_llm, critic_llm)
    console.print("[green]✓[/green] Agents initialized\n")
    
    # Run workflow
    console.print("[bold cyan]🎭 Performer is generating a joke...[/bold cyan]")
    result = workflow.run(prompt)
    
    # Display joke
    console.print("\n")
    console.print(Panel(
        result["joke"],
        title="[bold green]🎭 Generated Joke[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    
    # Display feedback
    feedback = result["feedback"]
    
    console.print("\n[bold cyan]🧐 Critic's Evaluation[/bold cyan]\n")
    
    # Metrics table
    metrics_table = Table(show_header=False, box=None)
    metrics_table.add_column("Metric", style="bold")
    metrics_table.add_column("Value")
    
    score = feedback["laughability_score"]
    score_emoji = "🔥" if score >= 80 else "😄" if score >= 60 else "😐" if score >= 40 else "😬"
    
    metrics_table.add_row("Laughability Score", f"{score_emoji} {score}/100")
    metrics_table.add_row("Age Appropriateness", feedback["age_appropriateness"])
    
    console.print(metrics_table)
    console.print()
    
    # Strengths
    console.print("[bold green]💪 Strengths:[/bold green]")
    for strength in feedback["strengths"]:
        console.print(f"  • {strength}")
    console.print()
    
    # Weaknesses
    console.print("[bold yellow]⚠️  Weaknesses:[/bold yellow]")
    for weakness in feedback["weaknesses"]:
        console.print(f"  • {weakness}")
    console.print()
    
    # Suggestions
    console.print("[bold blue]💡 Suggestions:[/bold blue]")
    for suggestion in feedback["suggestions"]:
        console.print(f"  • {suggestion}")
    console.print()
    
    # Overall verdict
    console.print(Panel(
        feedback["overall_verdict"],
        title="[bold]📝 Overall Verdict[/bold]",
        border_style="blue"
    ))
    
    # LangSmith info
    console.print(f"\n[dim]🔍 This run has been traced in LangSmith project: {settings.langchain_project}[/dim]")


if __name__ == "__main__":
    main()

