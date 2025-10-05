#!/usr/bin/env python3
"""
Main entry point for Resume Parser & Knowledge Graph Builder
"""

import sys
import os
import subprocess

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point"""
    try:
        # Check if streamlit is installed
        subprocess.run([sys.executable, "-c", "import streamlit"], check=True)
        
        # Run the app
        print("🚀 Starting Resume Parser & Knowledge Graph Builder...")
        print("📄 Open your browser to http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except subprocess.CalledProcessError:
        print("❌ Error: Streamlit is not installed.")
        print("💡 Please run: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
