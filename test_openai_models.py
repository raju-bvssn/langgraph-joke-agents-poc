#!/usr/bin/env python3
"""
Diagnostic script to test OpenAI model detection.
Shows which models are available on your OpenAI account.
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.llm import fetch_openai_models
from app.utils.settings import settings
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def main():
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🔍 OpenAI Model Detection Test[/bold cyan]\n"
        "[dim]Detecting models available on your OpenAI account[/dim]",
        border_style="cyan"
    ))
    
    # Check API key
    console.print("\n[bold]Checking API Key:[/bold]")
    if not settings.openai_api_key:
        console.print("[red]❌ No OpenAI API key found[/red]")
        console.print("[yellow]Please set OPENAI_API_KEY in your .env file[/yellow]")
        return 1
    
    if settings.openai_api_key.startswith("sk-your"):
        console.print("[yellow]⚠️  Placeholder API key detected[/yellow]")
        console.print("[yellow]Please replace with your actual OpenAI API key[/yellow]")
        return 1
    
    console.print(f"[green]✅ API key found[/green] (starts with: {settings.openai_api_key[:10]}...)")
    
    # Fetch models
    console.print("\n[bold]Fetching available models from OpenAI API...[/bold]")
    
    try:
        models = fetch_openai_models()
        
        if not models:
            console.print("[red]❌ No models detected[/red]")
            return 1
        
        console.print(f"\n[bold green]✅ Detected {len(models)} chat-capable models:[/bold green]\n")
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim")
        table.add_column("Model ID", style="cyan")
        table.add_column("Category", style="yellow")
        
        for idx, model_id in enumerate(models, 1):
            # Categorize model
            if model_id.startswith("o3"):
                category = "O3 Series (Latest)"
            elif model_id.startswith("o1") and "mini" not in model_id:
                category = "O1 Series"
            elif model_id.startswith("o1-mini"):
                category = "O1 Mini"
            elif model_id.startswith("gpt-4o") and "mini" not in model_id:
                category = "GPT-4o"
            elif model_id.startswith("gpt-4o-mini"):
                category = "GPT-4o Mini"
            elif model_id.startswith("gpt-4-turbo"):
                category = "GPT-4 Turbo"
            elif model_id.startswith("gpt-4"):
                category = "GPT-4"
            elif model_id.startswith("gpt-3.5-turbo"):
                category = "GPT-3.5 Turbo"
            else:
                category = "Other"
            
            table.add_row(str(idx), model_id, category)
        
        console.print(table)
        
        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  • Total models detected: {len(models)}")
        console.print(f"  • These models will appear in the Streamlit UI dropdowns")
        console.print(f"  • Models are sorted by capability (most capable first)")
        
        # Usage tip
        console.print("\n[bold cyan]💡 Usage:[/bold cyan]")
        console.print("  Run the Streamlit app to see these models in action:")
        console.print("  [dim]streamlit run app/main.py[/dim]")
        
        return 0
        
    except Exception as e:
        console.print(f"\n[red]❌ Error fetching models:[/red] {str(e)}")
        console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())

