"""GraphQL client for GitLab API using the gql library.

This module provides a GraphQL client for GitLab's GraphQL API,
specifically designed for Work Items API migration.
"""

import os
from typing import Any

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport

from .custom_exceptions import GitLabAPIError, GitLabAuthError, GitLabErrorType

# Constants
MAX_QUERY_LOG_LENGTH = 200


class GitLabGraphQLClient:
    """GraphQL client for GitLab API using the gql library.

    Provides a convenient wrapper around the gql library for GitLab GraphQL operations,
    particularly for Work Items functionality.
    """

    def __init__(self, base_url: str | None = None, token: str | None = None):
        """Initialize the GraphQL client.

        Args:
            base_url: GitLab instance base URL (e.g., 'https://gitlab.com').
                     If None, uses GITLAB_API_URL environment variable.
            token: GitLab personal access token. If None, uses GITLAB_PERSONAL_ACCESS_TOKEN.
        """
        self.base_url = (base_url or os.getenv("GITLAB_API_URL", "https://gitlab.com")).rstrip('/')
        self.token = token or os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")

        # Don't validate token during init - validate when actually used

        self.graphql_url = f"{self.base_url}/api/graphql"

        # Initialize client as None - will be created when first used
        self.transport = None
        self.client = None

    def _ensure_client(self):
        """Ensure the GraphQL client is initialized with proper authentication."""
        if self.client is None:
            if not self.token:
                raise GitLabAuthError()

            # Configure transport with authentication
            headers = {
                "Authorization": f"Bearer {self.token}",
            }

            self.transport = HTTPXAsyncTransport(
                url=self.graphql_url,
                headers=headers,
                timeout=30.0
            )

            # Create gql client with schema fetching disabled for performance
            self.client = Client(
                transport=self.transport,
                fetch_schema_from_transport=False,  # Disable for performance
                execute_timeout=30.0
            )

    async def execute(self, query_string: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query or mutation.

        Args:
            query_string: GraphQL query or mutation string
            variables: Query/mutation variables dictionary

        Returns:
            dict: GraphQL response data

        Raises:
            GitLabAPIError: If the query fails or returns errors
        """
        try:
            # Ensure client is initialized
            self._ensure_client()

            # Parse the query string
            query = gql(query_string)

            # Execute the query using the client
            async with self.client as session:
                result = await session.execute(query, variable_values=variables or {})
                return result

        except Exception as exc:
            # Handle GraphQL errors and convert to GitLabAPIError
            error_message = str(exc)

            if "GraphQLError" in error_message or "errors" in error_message.lower():
                raise GitLabAPIError(
                    GitLabErrorType.REQUEST_FAILED,
                    {
                        "message": f"GraphQL execution failed: {error_message}",
                        "query": query_string[:MAX_QUERY_LOG_LENGTH] + "..." if len(query_string) > MAX_QUERY_LOG_LENGTH else query_string,
                        "variables": variables,
                    }
                ) from exc
            elif "timeout" in error_message.lower():
                raise GitLabAPIError(
                    GitLabErrorType.REQUEST_FAILED,
                    {
                        "message": "GraphQL request timed out",
                        "operation": "graphql_execute",
                    }
                ) from exc
            elif "unauthorized" in error_message.lower() or "401" in error_message:
                raise GitLabAPIError(
                    GitLabErrorType.PERMISSION_DENIED,
                    {
                        "message": "GraphQL authentication failed",
                        "operation": "graphql_execute",
                    }
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.SERVER_ERROR,
                    {
                        "message": f"Unexpected error during GraphQL execution: {error_message}",
                        "operation": "graphql_execute",
                    }
                ) from exc

    async def query(self, query_string: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query.

        This is an alias for execute() to provide semantic clarity for queries.

        Args:
            query_string: GraphQL query string
            variables: Query variables dictionary

        Returns:
            dict: GraphQL response data
        """
        return await self.execute(query_string, variables)

    async def mutation(self, mutation_string: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL mutation.

        This is an alias for execute() to provide semantic clarity for mutations.

        Args:
            mutation_string: GraphQL mutation string
            variables: Mutation variables dictionary

        Returns:
            dict: GraphQL response data
        """
        return await self.execute(mutation_string, variables)

    async def close(self):
        """Close the transport connection."""
        await self.transport.close()


# Singleton GraphQL client instance
_graphql_client: GitLabGraphQLClient | None = None


def initialize_graphql_client(base_url: str | None = None, token: str | None = None) -> GitLabGraphQLClient:
    """Initialize the global GraphQL client instance.

    Args:
        base_url: GitLab instance base URL (optional, uses env var if not provided)
        token: GitLab authentication token (optional, uses env var if not provided)

    Returns:
        GitLabGraphQLClient: The initialized client
    """
    global _graphql_client
    _graphql_client = GitLabGraphQLClient(base_url, token)
    return _graphql_client


def get_graphql_client() -> GitLabGraphQLClient:
    """Get the global GraphQL client instance.

    Auto-initializes the client if not already initialized.

    Returns:
        GitLabGraphQLClient: The client instance

    Raises:
        GitLabAuthError: If authentication token is not available
    """
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = GitLabGraphQLClient()
    return _graphql_client


# Singleton instance for global use (like REST client) - lazy initialization
gitlab_graphql_client = None
