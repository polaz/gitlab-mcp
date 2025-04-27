"""Search tools for GitLab MCP.

This module provides search tools for GitLab resources through the MCP server.
"""

import asyncio
from typing import Any

from src.api.rest_client import GitLabRestClient
from src.schemas.search import (
    BlobSearchFilters,
    SearchScope,
)
from src.services.search import SearchService


class SearchError(ValueError):
    """Raised when a search operation fails."""

    INVALID_PARAMETERS = "Invalid search parameters"
    UNSUPPORTED_SCOPE = "Unsupported search scope"
    UNSUPPORTED_GROUP_SCOPE = "Unsupported scope for group search"

    def __init__(
        self, error_type: str = INVALID_PARAMETERS, cause: Exception | None = None
    ) -> None:
        """Initialize a new search error.

        Args:
            error_type: The type of search error.
            cause: The underlying exception that caused this error.
        """
        super().__init__(error_type)
        self.cause = cause


async def _get_search_service() -> SearchService:
    """Get a configured search service instance.

    Returns:
        A search service instance.
    """
    client = GitLabRestClient()
    return SearchService(client)


def _sanitize_user_data(data: dict[str, Any]) -> dict[str, Any]:
    """Remove personal information from user data.

    Args:
        data: The user data to sanitize.

    Returns:
        The sanitized user data.
    """
    if not isinstance(data, dict):
        return data

    result = data.copy()

    # Remove personal information
    for field in ["email", "name", "avatar_url"]:
        if field in result:
            result[field] = "[REDACTED]"

    # Keep only essential user info
    if "author" in result and isinstance(result["author"], dict):
        result["author"] = {
            "id": result["author"].get("id"),
            "username": result["author"].get("username"),
        }

    if (
        "assignee" in result
        and isinstance(result["assignee"], dict)
        and result["assignee"]
    ):
        result["assignee"] = {
            "id": result["assignee"].get("id"),
            "username": result["assignee"].get("username"),
        }

    if "assignees" in result and isinstance(result["assignees"], list):
        result["assignees"] = [
            {"id": user.get("id"), "username": user.get("username")}
            for user in result["assignees"]
            if isinstance(user, dict)
        ]

    return result


def _sanitize_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sanitize a list of results to remove personal information.

    Args:
        results: The list of results to sanitize.

    Returns:
        The sanitized results.
    """
    return [_sanitize_user_data(result) for result in results]


def _setup_async_search() -> tuple[asyncio.AbstractEventLoop, SearchService]:
    """Set up the async environment for search operations.

    Returns:
        A tuple containing the event loop and search service.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    search_service = loop.run_until_complete(_get_search_service())
    return loop, search_service


def _search_project_by_type(
    loop: asyncio.AbstractEventLoop,
    search_service: SearchService,
    project_id: str,
    search_term: str,
    scope_enum: SearchScope,
    ref: str | None = None,
    blob_filters: BlobSearchFilters | None = None,
) -> list[dict]:
    """Execute a search in a project with proper typing based on scope.

    Args:
        loop: The event loop to use.
        search_service: The search service instance.
        project_id: The project ID or path.
        search_term: The term to search for.
        scope_enum: The search scope.
        ref: Optional reference (branch, tag) to search in.
        blob_filters: Optional filters for blob searches.

    Returns:
        The search results as dictionaries.

    Raises:
        SearchError: If the search scope is not supported.
    """
    # Handle different cases separately based on scope
    if scope_enum == SearchScope.BLOBS and blob_filters:
        results = loop.run_until_complete(
            search_service.search_project(
                project_id, search_term, SearchScope.BLOBS, ref, blob_filters
            )
        )
    elif scope_enum == SearchScope.WIKI_BLOBS:
        results = loop.run_until_complete(
            search_service.search_project(
                project_id, search_term, SearchScope.WIKI_BLOBS
            )
        )
    elif scope_enum == SearchScope.COMMITS and ref:
        results = loop.run_until_complete(
            search_service.search_project(
                project_id, search_term, SearchScope.COMMITS, ref
            )
        )
    elif scope_enum == SearchScope.ISSUES:
        results = loop.run_until_complete(
            search_service.search_project(project_id, search_term, SearchScope.ISSUES)
        )
    elif scope_enum == SearchScope.MERGE_REQUESTS:
        results = loop.run_until_complete(
            search_service.search_project(
                project_id, search_term, SearchScope.MERGE_REQUESTS
            )
        )
    elif scope_enum == SearchScope.MILESTONES:
        results = loop.run_until_complete(
            search_service.search_project(
                project_id, search_term, SearchScope.MILESTONES
            )
        )
    elif scope_enum == SearchScope.USERS:
        results = loop.run_until_complete(
            search_service.search_project(project_id, search_term, SearchScope.USERS)
        )
    elif scope_enum == SearchScope.NOTES:
        results = loop.run_until_complete(
            search_service.search_project(project_id, search_term, SearchScope.NOTES)
        )
    else:
        raise SearchError(SearchError.UNSUPPORTED_SCOPE)

    return [result.dict() for result in results]


def search_global_tool(search_term: str, scope: str) -> dict:
    """Search across all GitLab resources.

    Args:
        search_term (str): The term to search for.
        scope (str): The scope to search in (projects, issues, merge_requests, etc).

    Returns:
        dict: The search results, including:
            - scope (str): The search scope.
            - search_term (str): The search term.
            - results (list[dict]): The sanitized search results.
            - count (int): The number of results.

    Raises:
        SearchError: If the search parameters are invalid.
    """
    try:
        # Convert string scope to enum
        scope_enum = SearchScope(scope)

        # Execute search
        loop, search_service = _setup_async_search()
        results = loop.run_until_complete(
            search_service.search_globally(search_term, scope_enum)  # type: ignore[arg-type]
        )

        # Convert results to dict and sanitize
        results_dict = [result.dict() for result in results]
        sanitized_results = _sanitize_results(results_dict)

        return {
            "scope": scope,
            "search_term": search_term,
            "results": sanitized_results,
            "count": len(sanitized_results),
        }
    except ValueError as e:
        raise SearchError(SearchError.INVALID_PARAMETERS, e) from e


def search_project_tool(
    project_id: str,
    search_term: str,
    scope: str,
    ref: str | None = None,
    filename: str | None = None,
    path: str | None = None,
    extension: str | None = None,
) -> dict:
    """Search within a specific project.

    Args:
        project_id (str): The project ID or path.
        search_term (str): The term to search for.
        scope (str): The scope to search in (issues, merge_requests, etc).
        ref (str, optional): Branch or tag to search in (for blobs/commits).
        filename (str, optional): Filter blobs by filename pattern.
        path (str, optional): Filter blobs by path pattern.
        extension (str, optional): Filter blobs by file extension.

    Returns:
        dict: The search results, including:
            - project_id (str): The project ID or path.
            - scope (str): The search scope.
            - search_term (str): The search term.
            - ref (str | None): The reference used for the search.
            - filters (dict | None): The filters used (filename, path, extension).
            - results (list[dict]): The sanitized search results.
            - count (int): The number of results.

    Raises:
        SearchError: If the scope is invalid.
    """
    try:
        # Convert string scope to enum
        scope_enum = SearchScope(scope)

        # Set up blob filters if needed
        blob_filters = None
        if any([filename, path, extension]):
            blob_filters = BlobSearchFilters(
                filename=filename, path=path, extension=extension
            )

        # Set up search environment
        loop, search_service = _setup_async_search()

        # Execute search with proper typing
        results_dict = _search_project_by_type(
            loop, search_service, project_id, search_term, scope_enum, ref, blob_filters
        )

        # Sanitize results
        sanitized_results = _sanitize_results(results_dict)

        return {
            "project_id": project_id,
            "scope": scope,
            "search_term": search_term,
            "ref": ref,
            "filters": {"filename": filename, "path": path, "extension": extension}
            if any([filename, path, extension])
            else None,
            "results": sanitized_results,
            "count": len(sanitized_results),
        }
    except ValueError as e:
        raise SearchError(SearchError.INVALID_PARAMETERS, e) from e


def _search_group_by_type(
    loop: asyncio.AbstractEventLoop,
    search_service: SearchService,
    group_id: str,
    search_term: str,
    scope_enum: SearchScope,
) -> list[dict]:
    """Execute a search in a group with proper typing based on scope.

    Args:
        loop: The event loop to use.
        search_service: The search service instance.
        group_id: The group ID or path.
        search_term: The term to search for.
        scope_enum: The search scope.

    Returns:
        The search results as dictionaries.

    Raises:
        SearchError: If the search scope is not supported.
    """
    if scope_enum == SearchScope.PROJECTS:
        results = loop.run_until_complete(
            search_service.search_group(group_id, search_term, SearchScope.PROJECTS)
        )
    elif scope_enum == SearchScope.ISSUES:
        results = loop.run_until_complete(
            search_service.search_group(group_id, search_term, SearchScope.ISSUES)
        )
    elif scope_enum == SearchScope.MERGE_REQUESTS:
        results = loop.run_until_complete(
            search_service.search_group(
                group_id, search_term, SearchScope.MERGE_REQUESTS
            )
        )
    elif scope_enum == SearchScope.MILESTONES:
        results = loop.run_until_complete(
            search_service.search_group(group_id, search_term, SearchScope.MILESTONES)
        )
    else:
        raise SearchError(SearchError.UNSUPPORTED_GROUP_SCOPE)

    return [result.dict() for result in results]


def search_group_tool(group_id: str, search_term: str, scope: str) -> dict:
    """Search within a specific group.

    Args:
        group_id (str): The group ID or path.
        search_term (str): The term to search for.
        scope (str): The scope to search in (projects, issues, etc).

    Returns:
        dict: The search results, including:
            - group_id (str): The group ID or path.
            - scope (str): The search scope.
            - search_term (str): The search term.
            - results (list[dict]): The sanitized search results.
            - count (int): The number of results.

    Raises:
        SearchError: If the scope is invalid.
    """
    try:
        # Convert string scope to enum
        scope_enum = SearchScope(scope)

        # Set up search environment
        loop, search_service = _setup_async_search()

        # Execute search with proper typing
        results_dict = _search_group_by_type(
            loop, search_service, group_id, search_term, scope_enum
        )

        # Sanitize results
        sanitized_results = _sanitize_results(results_dict)

        return {
            "group_id": group_id,
            "scope": scope,
            "search_term": search_term,
            "results": sanitized_results,
            "count": len(sanitized_results),
        }
    except ValueError as e:
        raise SearchError(SearchError.INVALID_PARAMETERS, e) from e
