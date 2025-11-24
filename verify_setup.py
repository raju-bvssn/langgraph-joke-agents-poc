#!/usr/bin/env python3
"""
Verification script to check if the POC is properly set up.
Runs before starting the application to catch configuration issues.
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro}"


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    return env_path.exists(), str(env_path)


def check_dependencies():
    """Check if key dependencies are installed"""
    required = {
        "langchain": "langchain",
        "langgraph": "langgraph",
        "langsmith": "langsmith",
        "streamlit": "streamlit",
        "pydantic": "pydantic",
    }
    
    installed = {}
    for name, package in required.items():
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            installed[name] = (True, version)
        except ImportError:
            installed[name] = (False, "not installed")
    
    return installed


def check_api_keys():
    """Check if API keys are configured"""
    try:
        from app.utils.settings import settings
        
        checks = {
            "OpenAI Key": bool(settings.openai_api_key and settings.openai_api_key != "sk-your-openai-key-here"),
            "Groq Key": bool(settings.groq_api_key and settings.groq_api_key != "gsk-your-groq-key-here"),
            "LangSmith Key": bool(settings.langchain_api_key and settings.langchain_api_key != "ls-your-langsmith-key-here"),
        }
        
        provider_ok = False
        if settings.llm_provider == "openai" and checks["OpenAI Key"]:
            provider_ok = True
        elif settings.llm_provider == "groq" and checks["Groq Key"]:
            provider_ok = True
        
        return checks, provider_ok, settings.llm_provider
    except Exception as e:
        return {}, False, str(e)


def check_project_structure():
    """Verify project structure is correct"""
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/agents/__init__.py",
        "app/agents/performer.py",
        "app/agents/critic.py",
        "app/graph/__init__.py",
        "app/graph/workflow.py",
        "app/utils/__init__.py",
        "app/utils/settings.py",
        "app/utils/llm.py",
        "requirements.txt",
        "README.md",
    ]
    
    results = {}
    for file_path in required_files:
        path = Path(file_path)
        results[file_path] = path.exists()
    
    return results


def main():
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🔍 LangGraph Joke Agents - Setup Verification[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    all_passed = True
    
    # Check Python version
    py_ok, py_version = check_python_version()
    if py_ok:
        console.print(f"✅ Python version: [green]{py_version}[/green] (>= 3.10)")
    else:
        console.print(f"❌ Python version: [red]{py_version}[/red] (requires >= 3.10)")
        all_passed = False
    
    # Check .env file
    env_ok, env_path = check_env_file()
    if env_ok:
        console.print(f"✅ Environment file: [green]{env_path}[/green] found")
    else:
        console.print(f"⚠️  Environment file: [yellow]{env_path}[/yellow] not found")
        console.print(f"   [dim]Run: cp env.example .env[/dim]")
        all_passed = False
    
    console.print()
    
    # Check dependencies
    console.print("[bold]📦 Dependencies:[/bold]")
    deps = check_dependencies()
    
    deps_table = Table(show_header=True)
    deps_table.add_column("Package")
    deps_table.add_column("Status")
    deps_table.add_column("Version")
    
    for name, (installed, version) in deps.items():
        if installed:
            deps_table.add_row(name, "✅ Installed", f"[green]{version}[/green]")
        else:
            deps_table.add_row(name, "❌ Missing", f"[red]{version}[/red]")
            all_passed = False
    
    console.print(deps_table)
    console.print()
    
    # Check API keys
    console.print("[bold]🔑 API Keys:[/bold]")
    keys, provider_ok, provider = check_api_keys()
    
    if isinstance(keys, dict):
        keys_table = Table(show_header=True)
        keys_table.add_column("Key")
        keys_table.add_column("Status")
        
        for key_name, is_set in keys.items():
            if is_set:
                keys_table.add_row(key_name, "[green]✓ Configured[/green]")
            else:
                keys_table.add_row(key_name, "[yellow]✗ Not set[/yellow]")
        
        console.print(keys_table)
        
        if provider_ok:
            console.print(f"\n✅ LLM Provider: [green]{provider}[/green] is properly configured")
        else:
            console.print(f"\n❌ LLM Provider: [red]{provider}[/red] requires API key")
            all_passed = False
        
        if not keys["LangSmith Key"]:
            console.print("⚠️  [yellow]LangSmith key not set - tracing will be disabled[/yellow]")
    else:
        console.print(f"❌ [red]Error checking keys: {provider}[/red]")
        all_passed = False
    
    console.print()
    
    # Check project structure
    console.print("[bold]📁 Project Structure:[/bold]")
    structure = check_project_structure()
    
    missing_files = [f for f, exists in structure.items() if not exists]
    if missing_files:
        console.print(f"❌ [red]Missing files:[/red]")
        for f in missing_files:
            console.print(f"   - {f}")
        all_passed = False
    else:
        console.print("✅ [green]All required files present[/green]")
    
    console.print()
    console.print("─" * 60)
    
    # Final verdict
    if all_passed:
        console.print(Panel(
            "[bold green]✅ All checks passed! You're ready to run the application.[/bold green]\n\n"
            "Start the app with:\n"
            "[cyan]streamlit run app/main.py[/cyan]",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel(
            "[bold red]❌ Some checks failed. Please fix the issues above.[/bold red]\n\n"
            "Common fixes:\n"
            "1. Install dependencies: [cyan]pip install -r requirements.txt[/cyan]\n"
            "2. Create .env file: [cyan]cp env.example .env[/cyan]\n"
            "3. Add your API keys to the .env file",
            border_style="red"
        ))
        return 1


if __name__ == "__main__":
    sys.exit(main())

