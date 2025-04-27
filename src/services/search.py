"""Search service for GitLab API.

This module provides functions for searching across GitLab resources.
"""

from typing import Any, Literal, TypeVar, overload

from pydantic import BaseModel

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import GitLabRestClient
from src.schemas.search import (
    BlobSearchFilters,
    BlobSearchResult,
    CommitSearchResult,
    GlobalSearchRequest,
    GroupSearchRequest,
    IssueSearchResult,
    MergeRequestSearchResult,
    MilestoneSearchResult,
    NoteSearchResult,
    ProjectSearchRequest,
    ProjectSearchResult,
    SearchScope,
    UserSearchResult,
)

T = TypeVar("T", bound=BaseModel)


class SearchService:
    """Service for searching GitLab resources."""

    def __init__(self, client: GitLabRestClient) -> None:
        """Initialize the search service.

        Args:
            client: The GitLab REST client to use for API calls.
        """
        self._client = client

    @overload
    async def search_globally(
        self, search_term: str, scope: Literal[SearchScope.PROJECTS]
    ) -> list[ProjectSearchResult]: ...

    @overload
    async def search_globally(
        self, search_term: str, scope: Literal[SearchScope.ISSUES]
    ) -> list[IssueSearchResult]: ...

    @overload
    async def search_globally(
        self, search_term: str, scope: Literal[SearchScope.MERGE_REQUESTS]
    ) -> list[MergeRequestSearchResult]: ...

    @overload
    async def search_globally(
        self, search_term: str, scope: Literal[SearchScope.MILESTONES]
    ) -> list[MilestoneSearchResult]: ...

    @overload
    async def search_globally(
        self, search_term: str, scope: Literal[SearchScope.USERS]
    ) -> list[UserSearchResult]: ...

    @overload
    async def search_globally(
        self, search_term: str, scope: Literal[SearchScope.COMMITS]
    ) -> list[CommitSearchResult]: ...

    async def search_globally(self, search_term: str, scope: SearchScope) -> list[Any]:
        """Search across all resources in the GitLab instance.

        Args:
            search_term: The term to search for.
            scope: The scope to search in.

        Returns:
            A list of search results matching the scope and search term.

        Raises:
            GitLabAPIError: If the search operation fails.
        """
        try:
            search_request = GlobalSearchRequest(scope=scope, search=search_term)

            response = await self._client.get_async(
                "/search",
                params={
                    "scope": search_request.scope,
                    "search": search_request.search,
                },
            )

            return self._parse_search_results(response, scope)
        except GitLabAPIError as exc:
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {
                    "message": f"Failed to perform global search for term '{search_term}'",
                    "operation": "search_globally",
                    "scope": scope.value,
                },
            ) from exc
        except Exception as exc:
            raise GitLabAPIError(
                GitLabErrorType.SERVER_ERROR,
                {
                    "message": "Internal error performing global search",
                    "operation": "search_globally",
                    "scope": scope.value,
                },
            ) from exc

    @overload
    async def search_group(
        self, group_id: str, search_term: str, scope: Literal[SearchScope.PROJECTS]
    ) -> list[ProjectSearchResult]: ...

    @overload
    async def search_group(
        self, group_id: str, search_term: str, scope: Literal[SearchScope.ISSUES]
    ) -> list[IssueSearchResult]: ...

    @overload
    async def search_group(
        self,
        group_id: str,
        search_term: str,
        scope: Literal[SearchScope.MERGE_REQUESTS],
    ) -> list[MergeRequestSearchResult]: ...

    @overload
    async def search_group(
        self, group_id: str, search_term: str, scope: Literal[SearchScope.MILESTONES]
    ) -> list[MilestoneSearchResult]: ...

    @overload
    async def search_group(
        self, group_id: str, search_term: str, scope: SearchScope
    ) -> list[Any]: ...

    async def search_group(
        self, group_id: str, search_term: str, scope: SearchScope
    ) -> list[Any]:
        """Search within a specific group.

        Args:
            group_id: The ID or URL-encoded path of the group.
            search_term: The term to search for.
            scope: The scope to search in.

        Returns:
            A list of search results matching the scope and search term.

        Raises:
            GitLabAPIError: If the search operation fails.
        """
        try:
            search_request = GroupSearchRequest(
                group_id=group_id, scope=scope, search=search_term
            )

            response = await self._client.get_async(
                f"/groups/{search_request.group_id}/search",
                params={
                    "scope": search_request.scope,
                    "search": search_request.search,
                },
            )

            return self._parse_search_results(response, scope)
        except GitLabAPIError as exc:
            if "not found" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {group_id} not found"},
                ) from exc
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {
                    "message": f"Failed to search group {group_id} for term '{search_term}'",
                    "operation": "search_group",
                    "scope": scope.value,
                },
            ) from exc
        except Exception as exc:
            raise GitLabAPIError(
                GitLabErrorType.SERVER_ERROR,
                {
                    "message": "Internal error performing group search",
                    "operation": "search_group",
                    "scope": scope.value,
                },
            ) from exc

    @overload
    async def search_project(
        self, project_id: str, search_term: str, scope: Literal[SearchScope.ISSUES]
    ) -> list[IssueSearchResult]: ...

    @overload
    async def search_project(
        self,
        project_id: str,
        search_term: str,
        scope: Literal[SearchScope.MERGE_REQUESTS],
    ) -> list[MergeRequestSearchResult]: ...

    @overload
    async def search_project(
        self, project_id: str, search_term: str, scope: Literal[SearchScope.MILESTONES]
    ) -> list[MilestoneSearchResult]: ...

    @overload
    async def search_project(
        self, project_id: str, search_term: str, scope: Literal[SearchScope.USERS]
    ) -> list[UserSearchResult]: ...

    @overload
    async def search_project(
        self,
        project_id: str,
        search_term: str,
        scope: Literal[SearchScope.COMMITS],
        ref: str | None = None,
    ) -> list[CommitSearchResult]: ...

    @overload
    async def search_project(
        self,
        project_id: str,
        search_term: str,
        scope: Literal[SearchScope.BLOBS],
        ref: str | None = None,
        blob_filters: BlobSearchFilters | None = None,
    ) -> list[BlobSearchResult]: ...

    @overload
    async def search_project(
        self,
        project_id: str,
        search_term: str,
        scope: Literal[SearchScope.WIKI_BLOBS],
    ) -> list[BlobSearchResult]: ...

    @overload
    async def search_project(
        self,
        project_id: str,
        search_term: str,
        scope: Literal[SearchScope.NOTES],
    ) -> list[NoteSearchResult]: ...

    async def search_project(
        self,
        project_id: str,
        search_term: str,
        scope: SearchScope,
        ref: str | None = None,
        blob_filters: BlobSearchFilters | None = None,
    ) -> list[Any]:
        """Search within a specific project.

        Args:
            project_id: The ID or URL-encoded path of the project.
            search_term: The term to search for.
            scope: The scope to search in.
            ref: Optional branch or tag to search in (for blobs/commits).
            blob_filters: Optional filters for blob searches.

        Returns:
            A list of search results matching the scope and search term.

        Raises:
            GitLabAPIError: If the search operation fails.
        """
        try:
            search_request = ProjectSearchRequest(
                project_id=project_id, scope=scope, search=search_term, ref=ref
            )

            params = {
                "scope": search_request.scope,
                "search": search_request.search,
            }

            if ref:
                params["ref"] = ref

            if blob_filters and scope in (SearchScope.BLOBS, SearchScope.WIKI_BLOBS):
                if blob_filters.filename:
                    search_term = f"{search_term} filename:{blob_filters.filename}"
                    params["search"] = search_term

                if blob_filters.path:
                    search_term = f"{search_term} path:{blob_filters.path}"
                    params["search"] = search_term

                if blob_filters.extension:
                    search_term = f"{search_term} extension:{blob_filters.extension}"
                    params["search"] = search_term

            response = await self._client.get_async(
                f"/projects/{search_request.project_id}/search",
                params=params,
            )

            return self._parse_search_results(response, scope)
        except GitLabAPIError as exc:
            if "not found" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Project {project_id} not found"},
                ) from exc

            ref_info = f" (ref: {ref})" if ref else ""
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {
                    "message": f"Failed to search project {project_id}{ref_info} for term '{search_term}'",
                    "operation": "search_project",
                    "scope": scope.value,
                },
            ) from exc
        except Exception as exc:
            raise GitLabAPIError(
                GitLabErrorType.SERVER_ERROR,
                {
                    "message": "Internal error performing project search",
                    "operation": "search_project",
                    "scope": scope.value,
                },
            ) from exc

    def _parse_search_results(
        self, response: list[dict[str, Any]], scope: SearchScope
    ) -> list[Any]:
        """Parse search results based on the scope.

        Args:
            response: The raw API response.
            scope: The search scope.

        Returns:
            A list of typed search results.
        """
        result_map = {
            SearchScope.PROJECTS: ProjectSearchResult,
            SearchScope.ISSUES: IssueSearchResult,
            SearchScope.MERGE_REQUESTS: MergeRequestSearchResult,
            SearchScope.MILESTONES: MilestoneSearchResult,
            SearchScope.USERS: UserSearchResult,
            SearchScope.COMMITS: CommitSearchResult,
            SearchScope.BLOBS: BlobSearchResult,
            SearchScope.WIKI_BLOBS: BlobSearchResult,
            SearchScope.NOTES: NoteSearchResult,
        }

        model_class = result_map.get(scope)
        if model_class is None:
            raise ValueError(f"Unsupported search scope: {scope}")

        return [model_class.model_validate(item) for item in response]
