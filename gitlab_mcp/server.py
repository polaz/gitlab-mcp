"""
GitLab MCP Server module entry point.

Imports and runs the main MCP server from the root server.py file.
"""

import sys
from pathlib import Path

# Add the root directory to the path to import the main server
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Import the main function from the root server.py
try:
    from server import main
except ImportError as e:
    print(f"Error importing server: {e}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Root directory: {root_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

__all__ = ["main"]
