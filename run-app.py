#!/usr/bin/env python3
# run-app.py - Development launcher for ani-gui
# Execute this file to run ani-gui in development mode

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.absolute()

# Add the project root to Python path for imports
sys.path.insert(0, str(project_root))

def check_venv():
    """Check if we're in a virtual environment, if not inform user."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        venv_path = project_root / 'venv'
        if venv_path.exists():
            print("ℹ Virtual environment found but not activated.")
            print("To activate, run: source venv/bin/activate")
            print("Or: python3 run-app.py (from the activated venv)")
            return False
    return True

def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk, Gio
    except ImportError as e:
        print(f"✗ Error: Missing required GTK libraries: {e}")
        print("\nInstall on Ubuntu/Debian:")
        print("  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adwaita-1")
        print("\nOr use the virtual environment setup:")
        print("  bash setup-venv.sh")
        sys.exit(1)
    
    try:
        import requests
    except ImportError:
        print("✗ Error: 'requests' module not found")
        print("\nInstall with:")
        print("  pip install requests")
        print("\nOr use the virtual environment setup:")
        print("  bash setup-venv.sh")
        sys.exit(1)

def main():
    """Main entry point for development."""
    if not check_venv():
        # Still try to run, but user should know
        pass
    
    check_dependencies()
    
    try:
        from src.main import AniGuiApplication
    except ImportError as e:
        print(f"✗ Error: Could not import AniGuiApplication: {e}")
        print("Make sure you're running this from the ani-gui project directory")
        sys.exit(1)
    
    app = AniGuiApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())