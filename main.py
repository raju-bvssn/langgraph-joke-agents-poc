"""
Root-level entry point for Lovable deployment.
This file allows the project to be run with: streamlit run main.py
"""

if __name__ == "__main__":
    # Import and run the Streamlit app
    import sys
    from pathlib import Path
    
    # Ensure the project root is in the path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Import the main Streamlit app
    from app.main import main
    
    # Run the application
    main()

