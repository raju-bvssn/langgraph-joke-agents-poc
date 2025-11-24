#!/usr/bin/env python3
"""
Test script for all LLM providers.
Tests each provider and model combination to ensure they work correctly.
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.llm import get_llm
from app.utils.settings import settings, MODEL_CATALOG
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


def test_provider_model(console: Console, provider: str, model: str) -> dict:
    """
    Test a specific provider/model combination.
    
    Returns:
        dict with status, response, and error information
    """
    try:
        # Get LLM instance
        llm = get_llm(provider=provider, model=model, temperature=0.7)
        
        # Test with simple prompt
        response = llm.invoke("Say hello in one sentence.")
        
        # Extract text from response
        if hasattr(response, 'content'):
            text = response.content
        else:
            text = str(response)
        
        return {
            "status": "✅ PASS",
            "response": text[:50] + "..." if len(text) > 50 else text,
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)
        # Shorten error message
        if len(error_msg) > 100:
            error_msg = error_msg[:97] + "..."
        
        return {
            "status": "❌ FAIL",
            "response": None,
            "error": error_msg
        }


def main():
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🧪 Multi-Provider LLM Testing Suite[/bold cyan]\n"
        "[dim]Testing all configured LLM providers and models[/dim]",
        border_style="cyan"
    ))
    
    # Check which API keys are configured
    console.print("\n[bold]Checking API Keys:[/bold]")
    api_keys_status = {
        "OpenAI": "✅" if settings.openai_api_key and not settings.openai_api_key.startswith("sk-your") else "❌",
        "Groq": "✅" if settings.groq_api_key and not settings.groq_api_key.startswith("gsk-your") else "❌",
        "HuggingFace": "✅" if settings.huggingface_api_key and not settings.huggingface_api_key.startswith("hf_your") else "❌",
        "Together AI": "✅" if settings.together_api_key and settings.together_api_key != "your-together-key-here" else "❌",
        "DeepInfra": "✅" if settings.deepinfra_api_key and settings.deepinfra_api_key != "your-deepinfra-key-here" else "❌",
    }
    
    for provider_name, status in api_keys_status.items():
        console.print(f"  {status} {provider_name}")
    
    console.print("\n[yellow]⚠️  Only providers with valid API keys will be tested[/yellow]\n")
    
    # Test all providers and models
    results = []
    total_tests = sum(len(models) for models in MODEL_CATALOG.values())
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Testing models...", total=total_tests)
        
        for provider, models in MODEL_CATALOG.items():
            # Skip OpenAI dynamic models for this test - just use the static list
            if provider == "openai" and api_keys_status["OpenAI"] == "❌":
                for model in models:
                    progress.update(task, advance=1, description=f"[dim]Skipping {provider}/{model}[/dim]")
                    results.append({
                        "provider": provider,
                        "model": model,
                        "status": "⏭️  SKIP",
                        "response": None,
                        "error": "No valid API key"
                    })
                continue
            
            # Map provider names to API key status
            provider_key_map = {
                "openai": "OpenAI",
                "groq": "Groq",
                "huggingface": "HuggingFace",
                "together": "Together AI",
                "deepinfra": "DeepInfra",
            }
            
            # Skip provider if no API key
            if api_keys_status.get(provider_key_map.get(provider, ""), "❌") == "❌":
                for model in models:
                    progress.update(task, advance=1, description=f"[dim]Skipping {provider}/{model}[/dim]")
                    results.append({
                        "provider": provider,
                        "model": model,
                        "status": "⏭️  SKIP",
                        "response": None,
                        "error": "No valid API key"
                    })
                continue
            
            for model in models:
                progress.update(task, advance=1, description=f"[cyan]Testing {provider}/{model}[/cyan]")
                
                result = test_provider_model(console, provider, model)
                results.append({
                    "provider": provider,
                    "model": model,
                    **result
                })
    
    # Display results in table
    console.print("\n[bold]Test Results:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="yellow")
    table.add_column("Status", style="bold")
    table.add_column("Response / Error", style="dim")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for result in results:
        status_style = "green" if "PASS" in result["status"] else "red" if "FAIL" in result["status"] else "dim"
        
        response_text = result["response"] if result["response"] else result["error"] or "Skipped"
        
        table.add_row(
            result["provider"],
            result["model"][:40] + "..." if len(result["model"]) > 40 else result["model"],
            f"[{status_style}]{result['status']}[/{status_style}]",
            response_text
        )
        
        if "PASS" in result["status"]:
            passed += 1
        elif "FAIL" in result["status"]:
            failed += 1
        elif "SKIP" in result["status"]:
            skipped += 1
    
    console.print(table)
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]✅ Passed: {passed}[/green]")
    console.print(f"  [red]❌ Failed: {failed}[/red]")
    console.print(f"  [dim]⏭️  Skipped: {skipped}[/dim]")
    console.print(f"  [bold]Total: {len(results)}[/bold]")
    
    # Recommendations
    console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
    
    if passed > 0:
        console.print(f"  ✅ {passed} provider/model combinations are working!")
        console.print("  You can use these in the Streamlit UI now.")
    
    if failed > 0:
        console.print(f"  ⚠️  {failed} combinations failed - check error messages above")
    
    if skipped > 0:
        console.print(f"  ℹ️  {skipped} combinations skipped - add API keys to test them")
        console.print("  Run: cp env.example .env and edit .env with your API keys")
    
    # Provider-specific recommendations
    console.print("\n[bold]Free Provider Setup:[/bold]")
    if api_keys_status["Groq"] == "❌":
        console.print("  🆓 [cyan]Groq[/cyan]: Get free API key at https://console.groq.com/keys")
    if api_keys_status["HuggingFace"] == "❌":
        console.print("  🆓 [cyan]HuggingFace[/cyan]: Get free API key at https://huggingface.co/settings/tokens")
    if api_keys_status["Together AI"] == "❌":
        console.print("  🆓 [cyan]Together AI[/cyan]: Get free trial at https://api.together.xyz/settings/api-keys")
    if api_keys_status["DeepInfra"] == "❌":
        console.print("  🆓 [cyan]DeepInfra[/cyan]: Get free trial at https://deepinfra.com/dash/api_keys")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

