#!/usr/bin/env python3
"""
Comprehensive LLM Model Testing Script
Tests all models in MODEL_CATALOG for instantiation and functionality.
"""
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.llm import get_llm, get_performer_llm, get_critic_llm
from app.utils.settings import MODEL_CATALOG, DEPRECATED_MODELS, settings
from app.graph.workflow import JokeWorkflow
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


def test_model_instantiation() -> Tuple[List[str], List[str]]:
    """
    Test that each model in MODEL_CATALOG can be instantiated.
    
    Returns:
        Tuple of (successes, failures)
    """
    console.print("\n[bold cyan]═══ Testing Model Instantiation ═══[/bold cyan]\n")
    
    successes = []
    failures = []
    
    for provider, models in MODEL_CATALOG.items():
        console.print(f"\n[bold]Testing {provider.upper()} models:[/bold]")
        
        for model in models:
            try:
                llm = get_llm(provider=provider, model=model, temperature=0.7)
                console.print(f"  ✅ {provider}/{model} - [green]OK[/green]")
                successes.append(f"{provider}/{model}")
            except Exception as e:
                console.print(f"  ❌ {provider}/{model} - [red]FAILED[/red]: {str(e)}")
                failures.append(f"{provider}/{model}: {str(e)}")
    
    return successes, failures


def test_simple_generation(provider: str, model: str) -> bool:
    """
    Test that a model can actually generate text.
    
    Args:
        provider: LLM provider
        model: Model name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        llm = get_llm(provider=provider, model=model, temperature=0.7)
        
        # Simple test generation
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content="Say 'test passed' if you can read this.")])
        
        if response and response.content:
            return True
        return False
    except Exception as e:
        console.print(f"    [red]Generation failed: {str(e)}[/red]")
        return False


def test_agent_functionality() -> Tuple[List[str], List[str]]:
    """
    Test that each model works with Performer and Critic agents.
    
    Returns:
        Tuple of (successes, failures)
    """
    console.print("\n[bold cyan]═══ Testing Agent Functionality ═══[/bold cyan]\n")
    
    successes = []
    failures = []
    
    test_topic = "unit testing"
    test_joke = "Why do programmers prefer dark mode? Because light attracts bugs!"
    
    for provider, models in MODEL_CATALOG.items():
        console.print(f"\n[bold]Testing {provider.upper()} models with agents:[/bold]")
        
        for model in models:
            # Test as Performer
            try:
                from app.agents.performer import PerformerAgent
                llm = get_performer_llm(provider=provider, model=model)
                agent = PerformerAgent(llm)
                joke = agent.generate_joke(test_topic)
                
                if joke and len(joke) > 10:
                    console.print(f"  ✅ {provider}/{model} as Performer - [green]OK[/green]")
                    successes.append(f"{provider}/{model} (Performer)")
                else:
                    console.print(f"  ⚠️  {provider}/{model} as Performer - [yellow]Empty response[/yellow]")
                    failures.append(f"{provider}/{model} (Performer): Empty response")
            except Exception as e:
                console.print(f"  ❌ {provider}/{model} as Performer - [red]FAILED[/red]: {str(e)[:50]}")
                failures.append(f"{provider}/{model} (Performer): {str(e)[:100]}")
            
            # Test as Critic
            try:
                from app.agents.critic import CriticAgent
                llm = get_critic_llm(provider=provider, model=model)
                agent = CriticAgent(llm)
                feedback = agent.evaluate_joke(test_joke)
                
                if feedback and hasattr(feedback, 'laughability_score'):
                    console.print(f"  ✅ {provider}/{model} as Critic - [green]OK[/green] (Score: {feedback.laughability_score})")
                    successes.append(f"{provider}/{model} (Critic)")
                else:
                    console.print(f"  ⚠️  {provider}/{model} as Critic - [yellow]Invalid feedback[/yellow]")
                    failures.append(f"{provider}/{model} (Critic): Invalid feedback format")
            except Exception as e:
                console.print(f"  ❌ {provider}/{model} as Critic - [red]FAILED[/red]: {str(e)[:50]}")
                failures.append(f"{provider}/{model} (Critic): {str(e)[:100]}")
    
    return successes, failures


def test_workflow_combinations() -> Tuple[List[str], List[str]]:
    """
    Test complete workflow with different model combinations.
    
    Returns:
        Tuple of (successes, failures)
    """
    console.print("\n[bold cyan]═══ Testing Workflow Combinations ═══[/bold cyan]\n")
    
    successes = []
    failures = []
    
    test_prompt = "artificial intelligence"
    
    # Test key combinations
    test_combinations = [
        ("groq", "llama-3.3-70b-versatile", "groq", "llama-3.1-8b-instant"),
        ("groq", "llama-3.3-70b-versatile", "openai", "gpt-4o-mini"),
        ("openai", "gpt-4o-mini", "groq", "llama-3.3-70b-versatile"),
        ("openai", "gpt-4o-mini", "openai", "gpt-4o-mini"),
    ]
    
    for performer_prov, performer_mod, critic_prov, critic_mod in test_combinations:
        combo_name = f"Performer: {performer_prov}/{performer_mod} + Critic: {critic_prov}/{critic_mod}"
        
        try:
            performer_llm = get_performer_llm(provider=performer_prov, model=performer_mod)
            critic_llm = get_critic_llm(provider=critic_prov, model=critic_mod)
            
            workflow = JokeWorkflow(performer_llm, critic_llm)
            result = workflow.run(test_prompt)
            
            if result and "joke" in result and "feedback" in result:
                score = result["feedback"].get("laughability_score", 0)
                console.print(f"  ✅ {combo_name[:60]}... - [green]OK[/green] (Score: {score})")
                successes.append(combo_name)
            else:
                console.print(f"  ⚠️  {combo_name[:60]}... - [yellow]Incomplete result[/yellow]")
                failures.append(f"{combo_name}: Incomplete workflow result")
                
        except Exception as e:
            console.print(f"  ❌ {combo_name[:60]}... - [red]FAILED[/red]")
            console.print(f"     Error: {str(e)[:100]}")
            failures.append(f"{combo_name}: {str(e)[:150]}")
    
    return successes, failures


def display_deprecated_models():
    """Display information about deprecated models."""
    if not any(DEPRECATED_MODELS.values()):
        return
    
    console.print("\n[bold yellow]═══ Deprecated Models ═══[/bold yellow]\n")
    
    for provider, models in DEPRECATED_MODELS.items():
        if models:
            console.print(f"[bold]{provider.upper()}:[/bold]")
            for model in models:
                console.print(f"  ⚠️  [yellow]{model}[/yellow] - No longer supported")
    
    console.print("\n[dim]These models have been removed from MODEL_CATALOG and should not be used.[/dim]\n")


def generate_summary_table(
    instantiation_results: Tuple[List[str], List[str]],
    agent_results: Tuple[List[str], List[str]],
    workflow_results: Tuple[List[str], List[str]]
) -> None:
    """Generate a summary table of all test results."""
    
    console.print("\n[bold cyan]═══ Test Summary ═══[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Test Category", style="cyan")
    table.add_column("Passed", style="green")
    table.add_column("Failed", style="red")
    table.add_column("Total", style="blue")
    
    inst_pass, inst_fail = instantiation_results
    agent_pass, agent_fail = agent_results
    work_pass, work_fail = workflow_results
    
    table.add_row(
        "Model Instantiation",
        str(len(inst_pass)),
        str(len(inst_fail)),
        str(len(inst_pass) + len(inst_fail))
    )
    
    table.add_row(
        "Agent Functionality",
        str(len(agent_pass)),
        str(len(agent_fail)),
        str(len(agent_pass) + len(agent_fail))
    )
    
    table.add_row(
        "Workflow Combinations",
        str(len(work_pass)),
        str(len(work_fail)),
        str(len(work_pass) + len(work_fail))
    )
    
    total_pass = len(inst_pass) + len(agent_pass) + len(work_pass)
    total_fail = len(inst_fail) + len(agent_fail) + len(work_fail)
    
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_pass}[/bold green]",
        f"[bold red]{total_fail}[/bold red]",
        f"[bold]{total_pass + total_fail}[/bold]"
    )
    
    console.print(table)
    
    return total_pass, total_fail


def main():
    """Run all LLM tests."""
    
    console.print(Panel.fit(
        "[bold cyan]🧪 LangGraph Joke Agents - LLM Model Testing Suite[/bold cyan]\n"
        "[dim]Testing all models in MODEL_CATALOG for compatibility[/dim]",
        border_style="cyan"
    ))
    
    # Check API keys
    console.print("\n[bold]Checking API Keys:[/bold]")
    
    has_openai = bool(settings.openai_api_key)
    has_groq = bool(settings.groq_api_key)
    
    console.print(f"  OpenAI: {'✅ Set' if has_openai else '❌ Missing'}")
    console.print(f"  Groq: {'✅ Set' if has_groq else '❌ Missing'}")
    console.print(f"  LangSmith: {'✅ Set' if settings.langchain_api_key else '❌ Missing (optional)'}")
    
    if not has_openai and not has_groq:
        console.print("\n[red]❌ No API keys found! Please set at least one provider's API key in .env[/red]")
        sys.exit(1)
    
    # Display current model catalog
    console.print("\n[bold]Current Model Catalog:[/bold]")
    for provider, models in MODEL_CATALOG.items():
        console.print(f"  [cyan]{provider}:[/cyan] {', '.join(models)}")
    
    # Show deprecated models
    display_deprecated_models()
    
    # Run tests
    try:
        inst_results = test_model_instantiation()
        agent_results = test_agent_functionality()
        workflow_results = test_workflow_combinations()
        
        # Generate summary
        total_pass, total_fail = generate_summary_table(inst_results, agent_results, workflow_results)
        
        # Display failures in detail if any
        all_failures = inst_results[1] + agent_results[1] + workflow_results[1]
        
        if all_failures:
            console.print("\n[bold red]═══ Detailed Failures ═══[/bold red]\n")
            for i, failure in enumerate(all_failures, 1):
                console.print(f"[red]{i}.[/red] {failure}")
        
        # Final verdict
        console.print("\n" + "═" * 70 + "\n")
        
        if total_fail == 0:
            console.print(Panel(
                "[bold green]✅ ALL TESTS PASSED[/bold green]\n\n"
                f"Successfully tested {total_pass} configurations.\n"
                "All models in MODEL_CATALOG are working correctly!",
                border_style="green"
            ))
            return 0
        else:
            console.print(Panel(
                f"[bold red]❌ {total_fail} TEST(S) FAILED[/bold red]\n\n"
                f"Passed: {total_pass} | Failed: {total_fail}\n\n"
                "Please review the failures above and update MODEL_CATALOG accordingly.",
                border_style="red"
            ))
            return 1
            
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error:[/bold red] {str(e)}")
        console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())

