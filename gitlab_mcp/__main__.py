"""
Entry point for running GitLab MCP server as a module.

This allows the server to be run with:
    python -m gitlab_mcp
    uv run --with gitlab-mcp-server python -m gitlab_mcp
"""

from .server import main

if __name__ == "__main__":
    main()
