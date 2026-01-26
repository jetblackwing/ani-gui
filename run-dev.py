#!/usr/bin/env python3
# run-dev.py - Development launcher for ani-gui

import sys
import os

# Add src directory to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

if __name__ == '__main__':
    from ani_gui.main import main
    sys.exit(main(sys.argv))
