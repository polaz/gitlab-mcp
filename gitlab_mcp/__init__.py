"""
GitLab MCP Server - A Model Context Protocol server for GitLab API integration.

This package provides comprehensive tools for interacting with GitLab through
the modern Work Items GraphQL API and traditional REST endpoints.
"""

__version__ = "0.3.0"
__author__ = "Adit pal Singh, Dmitry Prudnikov"
__email__ = "mail@polaz.com"

from .server import main

__all__ = ["main"]
