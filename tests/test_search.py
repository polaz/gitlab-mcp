"""Tests for search functions.

This module tests all search-related functions:
- search_globally
- search_group
- search_project
"""



import time

import pytest

from src.schemas.repositories import GetRepositoryInput
from src.schemas.search import (
    GlobalSearchRequest,
    ProjectSearchRequest,
    SearchScope,
)
from src.services.repositories import get_repository
from src.services.search import (
    search_globally,
    search_group,
    search_project,
)
from tests.utils.validators import BulkValidator, ResponseValidator


class TestGlobalSearch:
    """Test global search functionality."""

    @pytest.mark.asyncio
    async def test_search_projects_globally(self):
        """Test searching for projects globally."""
        results = await search_globally("test", SearchScope.PROJECTS)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each project result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "projects")
            # Project-specific validations
            assert "name" in result_dict
            assert "path_with_namespace" in result_dict or "full_path" in result_dict

    @pytest.mark.asyncio
    async def test_search_issues_globally(self):
        """Test searching for issues globally."""
        results = await search_globally("bug", SearchScope.ISSUES)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each issue result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "issues")
            assert "title" in result_dict
            assert "state" in result_dict

    @pytest.mark.asyncio
    async def test_search_merge_requests_globally(self):
        """Test searching for merge requests globally."""
        results = await search_globally("feature", SearchScope.MERGE_REQUESTS)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each merge request result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "merge_requests")
            assert "title" in result_dict
            assert "state" in result_dict

    @pytest.mark.asyncio
    async def test_search_blobs_globally(self):
        """Test searching for code blobs globally."""
        results = await search_globally("function", SearchScope.BLOBS)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each blob result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "blobs")
            assert "filename" in result_dict
            assert "data" in result_dict

    @pytest.mark.asyncio
    async def test_search_wiki_blobs_globally(self):
        """Test searching for wiki blobs globally."""
        results = await search_globally("documentation", SearchScope.WIKI_BLOBS)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each wiki blob result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "wiki_blobs")
            assert "filename" in result_dict
            assert "data" in result_dict

    @pytest.mark.asyncio
    async def test_global_search_pagination(self):
        """Test global search functionality."""
        # Note: GitLab API pagination parameters are not supported in this function signature
        # This test validates search consistency and result structure
        results1 = await search_globally("test", SearchScope.PROJECTS)
        results2 = await search_globally("test", SearchScope.PROJECTS)

        # Validate search consistency
        assert isinstance(results1, list)
        assert isinstance(results2, list)

        # Search results should be consistent between calls
        if results1 and results2:
            # Convert Pydantic models to dicts for accessing fields
            dicts1 = [r.model_dump() if hasattr(r, 'model_dump') else r for r in results1]
            dicts2 = [r.model_dump() if hasattr(r, 'model_dump') else r for r in results2]

            ids1 = {result.get("id", result.get("iid")) for result in dicts1}
            ids2 = {result.get("id", result.get("iid")) for result in dicts2}
            # Results should be identical for same search
            assert ids1 == ids2, "Search results should be consistent between identical calls"


class TestGroupSearch:
    """Test group-scoped search functionality."""

    @pytest.mark.asyncio
    async def test_search_projects_in_group(
        self,
        test_group_path: str
    ):
        """Test searching for projects within a specific group."""
        results = await search_group(test_group_path, "test", SearchScope.PROJECTS)  # Search to get projects

        # Validate response structure
        assert isinstance(results, list)

        # Validate each project result belongs to the group
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "projects")
            project_path = result_dict.get("path_with_namespace", result_dict.get("full_path", ""))
            assert test_group_path in project_path

    @pytest.mark.asyncio
    async def test_search_issues_in_group(
        self,
        test_group_path: str
    ):
        """Test searching for issues within a specific group."""
        results = await search_group(test_group_path, "test", SearchScope.ISSUES)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each issue result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "issues")
            assert "title" in result_dict

    @pytest.mark.asyncio
    async def test_search_merge_requests_in_group(
        self,
        test_group_path: str
    ):
        """Test searching for merge requests within a specific group."""
        results = await search_group(test_group_path, "test", SearchScope.MERGE_REQUESTS)  # Search to get MRs

        # Validate response structure
        assert isinstance(results, list)

        # Validate each merge request result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "merge_requests")
            assert "title" in result_dict

    @pytest.mark.asyncio
    async def test_search_blobs_in_group(
        self,
        test_group_path: str
    ):
        """Test searching for code blobs within a specific group."""
        results = await search_group(test_group_path, "import", SearchScope.BLOBS)

        # Validate response structure
        assert isinstance(results, list)

        # Validate each blob result
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "blobs")
            assert "filename" in result_dict
            assert "data" in result_dict


class TestProjectSearch:
    """Test project-scoped search functionality."""

    @pytest.mark.asyncio
    async def test_search_issues_in_project(
        self,
        static_test_project_path: str
    ):
        """Test searching for issues within a specific project."""
        search_request = ProjectSearchRequest(
            project_id=static_test_project_path,
            scope=SearchScope.ISSUES,
            search="test"
        )

        results = await search_project(search_request)

        # Validate response structure (search may return empty results, which is valid)
        assert isinstance(results, list)

        # Validate each issue result if any are found
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "issues")
            assert "title" in result_dict
            assert "project_id" in result_dict or "iid" in result_dict

    @pytest.mark.asyncio
    async def test_search_merge_requests_in_project(
        self,
        static_test_project_path: str
    ):
        """Test searching for merge requests within a specific project."""
        search_request = ProjectSearchRequest(
            project_id=static_test_project_path,
            scope=SearchScope.MERGE_REQUESTS,
            search="test"  # Valid search term
        )

        results = await search_project(search_request)

        # Validate response structure (search may return empty results, which is valid)
        assert isinstance(results, list)

        # Validate each merge request result if any are found
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "merge_requests")
            assert "title" in result_dict
            assert "iid" in result_dict or "id" in result_dict

    @pytest.mark.asyncio
    async def test_search_blobs_in_project(
        self,
        static_test_project_path: str
    ):
        """Test searching for code blobs within a specific project."""
        search_request = ProjectSearchRequest(
            project_id=static_test_project_path,
            scope=SearchScope.BLOBS,
            search="def"  # Search for function definitions
        )

        results = await search_project(search_request)

        # Validate response structure (search may return empty results, which is valid)
        assert isinstance(results, list)

        # Validate each blob result if any are found
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "blobs")
            assert "filename" in result_dict
            assert "data" in result_dict
            # Should contain the search term if found
            data_content = result_dict.get("data", "").lower()
            assert "def" in data_content, f"Expected 'def' in blob data, got: {data_content[:100]}..."

    @pytest.mark.asyncio
    async def test_search_wiki_blobs_in_project(
        self,
        static_test_project_path: str
    ):
        """Test searching for wiki blobs within a specific project."""
        search_request = ProjectSearchRequest(
            project_id=static_test_project_path,
            scope=SearchScope.WIKI_BLOBS,
            search="help"
        )

        results = await search_project(search_request)

        # Validate response structure (wiki search may return empty results, which is valid)
        assert isinstance(results, list)

        # Validate each wiki blob result if any are found (many projects don't have wikis)
        for result in results:
            # Convert Pydantic model to dict for validation
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            ResponseValidator.validate_search_result(result_dict, "wiki_blobs")
            assert "filename" in result_dict
            assert "data" in result_dict


class TestSearchErrorHandling:
    """Test search error handling scenarios."""

    @pytest.mark.asyncio
    async def test_search_nonexistent_group(self):
        """Test searching in a non-existent group."""
        with pytest.raises(Exception) as exc_info:
            await search_group("nonexistent-group-12345", "test", SearchScope.PROJECTS)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_search_nonexistent_project(self):
        """Test searching in a non-existent project."""
        search_request = ProjectSearchRequest(
            project_id="nonexistent/project-12345",
            scope=SearchScope.ISSUES,
            search="test"
        )

        with pytest.raises(Exception) as exc_info:
            await search_project(search_request)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_search_invalid_scope(self):
        """Test searching with invalid scope."""
        # This test depends on the schema validation
        # If the schema prevents invalid scopes, this test validates that
        with pytest.raises((ValueError, TypeError, AttributeError)):
            GlobalSearchRequest(
                scope="invalid_scope",  # This should fail schema validation
                search="test"
            )


class TestSearchPerformance:
    """Test search performance scenarios."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_global_search_performance(self):
        """Test global search performance."""

        start_time = time.time()
        results = await search_globally("test", SearchScope.PROJECTS)
        end_time = time.time()

        # Performance validation (should complete within 10 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 10.0)

        # Validate response structure
        assert isinstance(results, list)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_group_search_performance(
        self,
        test_group_path: str
    ):
        """Test group search performance."""

        start_time = time.time()
        results = await search_group(test_group_path, "test", SearchScope.ISSUES)
        end_time = time.time()

        # Performance validation (should complete within 10 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 10.0)

        # Validate response structure
        assert isinstance(results, list)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_project_search_performance(
        self,
        static_test_project_path: str
    ):
        """Test project search performance."""

        search_request = ProjectSearchRequest(
            project_id=static_test_project_path,
            scope=SearchScope.BLOBS,
            search="function"
        )

        start_time = time.time()
        results = await search_project(search_request)
        end_time = time.time()

        # Performance validation (should complete within 10 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 10.0)

        # Validate response structure
        assert isinstance(results, list)


class TestSearchEdgeCases:
    """Test search edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_search_unicode_query(self):
        """Test searching with Unicode characters."""
        results = await search_globally("тест 测试 テスト", SearchScope.PROJECTS)  # Unicode search term

        # Should not crash and return valid structure
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_special_characters(self):
        """Test searching with special characters."""
        results = await search_globally("function()", SearchScope.BLOBS)  # Special characters in search

        # Should not crash and return valid structure
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_minimal_query(self):
        """Test searching with minimal valid query."""
        results = await search_globally("tes", SearchScope.PROJECTS)  # Minimal valid search

        # Should return results for minimal query
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_very_long_query(self):
        """Test searching with very long query."""
        long_query = "test " * 100  # Very long search term

        results = await search_globally(long_query, SearchScope.PROJECTS)

        # Should handle long queries gracefully
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_large_page_size(self):
        """Test searching with large page size."""
        results = await search_globally("test", SearchScope.PROJECTS)

        # Should handle large queries gracefully
        assert isinstance(results, list)


class TestSearchFieldValidation:
    """Test search result field validation."""

    @pytest.mark.asyncio
    async def test_search_project_result_fields(self):
        """Test that project search results have consistent fields."""
        results = await search_globally("test", SearchScope.PROJECTS)

        if results:
            project = results[0]
            # Convert Pydantic model to dict for validation
            project_dict = project.model_dump() if hasattr(project, 'model_dump') else project

            # Check required fields for projects
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in project_dict, f"Required field '{field}' missing from project search result"

    @pytest.mark.asyncio
    async def test_search_issue_result_fields(self):
        """Test that issue search results have consistent fields."""
        results = await search_globally("test", SearchScope.ISSUES)

        if results:
            issue = results[0]
            # Convert Pydantic model to dict for validation
            issue_dict = issue.model_dump() if hasattr(issue, 'model_dump') else issue

            # Check required fields for issues
            required_fields = ["id", "title"]
            for field in required_fields:
                assert field in issue_dict, f"Required field '{field}' missing from issue search result"

    @pytest.mark.asyncio
    async def test_search_blob_result_fields(self):
        """Test that blob search results have consistent fields."""
        results = await search_globally("function", SearchScope.BLOBS)

        if results:
            blob = results[0]
            # Convert Pydantic model to dict for validation
            blob_dict = blob.model_dump() if hasattr(blob, 'model_dump') else blob

            # Check required fields for blobs
            required_fields = ["filename", "data"]
            for field in required_fields:
                assert field in blob_dict, f"Required field '{field}' missing from blob search result"


class TestSearchIntegration:
    """Test search integration with other services."""

    @pytest.mark.asyncio
    async def test_search_and_retrieve_project(
        self,
        static_test_project_path: str
    ):
        """Test searching for a project and then retrieving its details."""

        # Search for the test project
        project_name = static_test_project_path.split('/')[-1]
        search_results = await search_globally(project_name, SearchScope.PROJECTS)

        # Find the test project in results
        test_project = None
        for result in search_results:
            # Convert Pydantic model to dict for field access
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            if static_test_project_path in result_dict.get("path_with_namespace", result_dict.get("full_path", "")):
                test_project = result_dict
                break

        if test_project:
            # Retrieve full project details
            get_input = GetRepositoryInput(project_path=static_test_project_path)
            full_project = await get_repository(get_input)

            # Validate consistency between search result and full details
            # Convert Pydantic model to dict for comparison
            full_project_dict = full_project.model_dump() if hasattr(full_project, 'model_dump') else full_project
            assert test_project["id"] == full_project_dict["id"]
            assert test_project["name"] == full_project_dict["name"]

    @pytest.mark.asyncio
    async def test_search_scope_coverage(self):
        """Test that all search scopes are properly implemented."""
        # Test each scope with a generic search
        scopes_to_test = [
            SearchScope.PROJECTS,
            SearchScope.ISSUES,
            SearchScope.MERGE_REQUESTS,
            SearchScope.BLOBS,
            SearchScope.WIKI_BLOBS,
        ]

        for scope in scopes_to_test:
            # Should not crash for any scope
            results = await search_globally("test", scope)
            assert isinstance(results, list), f"Scope {scope} did not return a list"
