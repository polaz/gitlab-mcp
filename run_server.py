#!/usr/bin/env python3
"""
Wrapper script to run the GitLab MCP server.
This ensures proper path resolution for Claude Desktop.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Change to the correct working directory
os.chdir(current_dir)

# Import and run the server
if __name__ == "__main__":
    import server
    server.mcp.run(transport="stdio")
