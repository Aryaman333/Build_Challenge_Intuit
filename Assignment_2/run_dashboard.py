"""Quick start script to launch the Streamlit dashboard."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "streamlit_app" / "app.py"
    
    print("=" * 70)
    print("Amazon Products Sales Analysis Dashboard")
    print("=" * 70)
    print(f"\nLaunching Streamlit app from: {app_path}")
    print("\nThe dashboard will open in your default browser at http://localhost:8501")
    print("\nPress Ctrl+C to stop the server when you're done.\n")
    print("=" * 70)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
