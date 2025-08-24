"""
Pytest configuration file for DTS Intraday AI Backtest System tests.
This file helps pytest discover and import modules from the src directory.
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add the src directory to Python path
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

