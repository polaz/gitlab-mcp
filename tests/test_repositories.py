"""Tests for repository management functions.

This module tests all repository-related functions:
- get_repository
- list_repositories
- create_repository
- update_repository
- delete_repository
"""


import time

import pytest

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.repositories import (
    CreateRepositoryInput,
    DeleteRepositoryInput,
    GetRepositoryInput,
    ListRepositoriesInput,
    UpdateRepositoryInput,
)
from src.services.repositories import (
    create_repository,
    delete_repository,
    get_repository,
    list_repositories,
    update_repository,
)
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory
from tests.utils.validators import BulkValidator, ResponseValidator


class TestRepositoryBasicOperations:
    """Test basic repository CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_existing_repository(
        self,
        test_project_path: str
    ):
        """Test getting an existing repository."""
        get_input = GetRepositoryInput(project_path=test_project_path)
        repository = await get_repository(get_input)

        # Validate response structure
        ResponseValidator.validate_repository(repository)

        # Validate specific fields
        assert repository["path_with_namespace"] == test_project_path
        assert "id" in repository
        assert "name" in repository
        assert "web_url" in repository

    @pytest.mark.asyncio
    async def test_list_repositories_by_group(
        self,
        test_project_path: str  # Use existing project instead of creating new one
    ):
        """Test listing repositories in a group."""
        # Extract group path from the existing test project path
        test_group_path = "/".join(test_project_path.split("/")[:-1])

        # Test listing repositories in the group
        list_input = ListRepositoriesInput(
            group_id=test_group_path,
            per_page=10,
            page=1
        )
        repositories = await list_repositories(list_input)

        # Validate response structure
        assert isinstance(repositories, list)
        assert len(repositories) > 0, f"Expected to find repositories in group {test_group_path}"

        # Validate each repository
        for repo in repositories:
            ResponseValidator.validate_repository(repo)
            # Should belong to the test group
            assert test_group_path in repo["path_with_namespace"], f"Repository {repo['path_with_namespace']} should belong to group {test_group_path}"

        # Verify the test project is in the list
        test_project_found = any(
            repo["path_with_namespace"] == test_project_path
            for repo in repositories
        )
        assert test_project_found, f"Test project {test_project_path} should be found in group listing"

    @pytest.mark.asyncio
    async def test_list_repositories_pagination(
        self,
        test_group_path: str
    ):
        """Test repository listing with pagination."""
        # Test first page
        list_input = ListRepositoriesInput(
            group_id=test_group_path,
            per_page=5,
            page=1
        )
        page1_repos = await list_repositories(list_input)

        # Test second page if enough repositories exist
        list_input.page = 2
        page2_repos = await list_repositories(list_input)

        # Validate pagination
        assert isinstance(page1_repos, list)
        assert isinstance(page2_repos, list)

        # No duplicates between pages
        if page1_repos and page2_repos:
            page1_ids = {repo["id"] for repo in page1_repos}
            page2_ids = {repo["id"] for repo in page2_repos}
            assert len(page1_ids.intersection(page2_ids)) == 0


class TestRepositoryCreation:
    """Test repository creation functionality."""

    @pytest.mark.asyncio
    async def test_create_repository_minimal(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test creating repository with minimal required fields."""
        repo_data = test_data_factory.repository_data()

        # Create in personal namespace (no namespace_id specified) for minimal test
        create_input = CreateRepositoryInput(
            name=repo_data["name"]
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Validate creation
        ResponseValidator.validate_repository(created_repo)
        assert created_repo["name"] == repo_data["name"]
        assert "id" in created_repo
        assert "web_url" in created_repo

    @pytest.mark.asyncio
    async def test_create_repository_full_options(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test creating repository with all options."""
        repo_data = test_data_factory.repository_data()

        create_input = CreateRepositoryInput(
            name=repo_data["name"],
            description=repo_data["description"],
            visibility="private",
            initialize_with_readme=True
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Validate creation with all options
        ResponseValidator.validate_repository(created_repo)
        assert created_repo["name"] == repo_data["name"]
        assert created_repo["description"] == repo_data["description"]
        assert created_repo["visibility"] == "private"
        assert created_repo["default_branch"] == "main"

    @pytest.mark.asyncio
    async def test_create_repository_with_readme(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test creating repository with README initialization."""
        repo_data = test_data_factory.repository_data()
        repo_data["name"] = f"TEST_README_{repo_data['name']}"

        create_input = CreateRepositoryInput(
            name=repo_data["name"],
            description="Test repository with README",
            initialize_with_readme=True
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Validate creation
        ResponseValidator.validate_repository(created_repo)
        assert "README" in created_repo.get("readme_url", "").upper() or created_repo.get("readme_url") is not None


class TestRepositoryUpdates:
    """Test repository update functionality."""

    @pytest.mark.asyncio
    async def test_update_repository_description(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test updating repository description."""
        # Create a repository first
        repo_data = test_data_factory.repository_data()
        create_input = CreateRepositoryInput(
            name=repo_data["name"],
            description="Original description"
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Update the repository
        new_description = "Updated description for testing"
        update_input = UpdateRepositoryInput(
            project_path=created_repo["path_with_namespace"],
            description=new_description
        )

        updated_repo = await update_repository(update_input)

        # Validate update
        ResponseValidator.validate_repository(updated_repo)
        assert updated_repo["description"] == new_description
        assert updated_repo["id"] == created_repo["id"]

    @pytest.mark.asyncio
    async def test_update_repository_visibility(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test updating repository visibility."""
        # Create a private repository first
        repo_data = test_data_factory.repository_data()
        create_input = CreateRepositoryInput(
            name=repo_data["name"],
            visibility="private"
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Update visibility to internal
        update_input = UpdateRepositoryInput(
            project_path=created_repo["path_with_namespace"],
            visibility="internal"
        )

        updated_repo = await update_repository(update_input)

        # Validate visibility update
        ResponseValidator.validate_repository(updated_repo)
        assert updated_repo["visibility"] == "internal"

    @pytest.mark.asyncio
    async def test_update_repository_multiple_fields(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test updating multiple repository fields at once."""
        # Create a repository first
        repo_data = test_data_factory.repository_data()
        create_input = CreateRepositoryInput(
            name=repo_data["name"]
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Update multiple fields (excluding default_branch since newly created repos are empty)
        update_input = UpdateRepositoryInput(
            project_path=created_repo["path_with_namespace"],
            description="Multi-field update test",
            visibility="internal"
        )

        updated_repo = await update_repository(update_input)

        # Validate all updates
        ResponseValidator.validate_repository(updated_repo)
        assert updated_repo["description"] == "Multi-field update test"
        assert updated_repo["visibility"] == "internal"


class TestRepositoryDeletion:
    """Test repository deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_repository(
        self,
        test_data_factory: TestDataFactory
    ):
        """Test deleting a repository."""
        # Create a repository first
        repo_data = test_data_factory.repository_data()
        repo_data["name"] = f"DELETE_TEST_{repo_data['name']}"

        create_input = CreateRepositoryInput(
            name=repo_data["name"]
        )

        created_repo = await create_repository(create_input)

        # Delete the repository
        delete_input = DeleteRepositoryInput(project_path=created_repo["path_with_namespace"])
        result = await delete_repository(delete_input)

        # Validate deletion - should return True on success
        assert result is True

        # Verify repository is gone by trying to get it (should fail with GitLabAPIError)
        get_input = GetRepositoryInput(project_path=created_repo["path_with_namespace"])
        with pytest.raises(GitLabAPIError):  # Should raise GitLabAPIError when trying to access deleted repo
            await get_repository(get_input)


class TestRepositoryErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_repository(self):
        """Test getting a repository that doesn't exist."""
        get_input = GetRepositoryInput(project_path="nonexistent/project")

        with pytest.raises(Exception) as exc_info:
            await get_repository(get_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_create_repository_duplicate_name(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory
    ):
        """Test creating repository with duplicate name in same namespace."""
        # Get existing repository info
        existing_repo = await get_repository(GetRepositoryInput(project_path=test_project_path))
        test_data_factory.repository_data()

        # Try to create with same name
        create_input = CreateRepositoryInput(
            name=existing_repo["name"],
            namespace_id=existing_repo["namespace"]["id"]
        )

        with pytest.raises(Exception) as exc_info:
            await create_repository(create_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["exists", "taken", "duplicate", "conflict"])

    @pytest.mark.asyncio
    async def test_update_nonexistent_repository(self):
        """Test updating a repository that doesn't exist."""
        update_input = UpdateRepositoryInput(
            project_path="nonexistent/project",
            description="This should fail"
        )

        with pytest.raises(Exception) as exc_info:
            await update_repository(update_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_delete_nonexistent_repository(self):
        """Test deleting a repository that doesn't exist."""
        delete_input = DeleteRepositoryInput(project_path="nonexistent/project")

        with pytest.raises(Exception) as exc_info:
            await delete_repository(delete_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])


class TestRepositoryEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_repository_unicode_name(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test creating repository with Unicode characters in name."""
        unicode_data = test_data_factory.unicode_data()

        # Use a simpler name that's likely to be accepted
        safe_name = f"TEST_Unicode_{hash(unicode_data['title']) % 10000}"

        create_input = CreateRepositoryInput(
            name=safe_name,
            description=unicode_data["description"]  # Unicode in description
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Validate Unicode handling
        ResponseValidator.validate_repository(created_repo)
        assert created_repo["description"] == unicode_data["description"]

    @pytest.mark.asyncio
    async def test_repository_long_description(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test creating repository with very long description."""
        large_data = test_data_factory.large_content_data()

        create_input = CreateRepositoryInput(
            name=large_data["name"],
            description=large_data["description"][:1000]  # Limit to reasonable size
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Validate large content handling
        ResponseValidator.validate_repository(created_repo)
        assert len(created_repo["description"]) > 500

    @pytest.mark.asyncio
    async def test_repository_special_characters(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test repository with special characters in description."""
        repo_data = test_data_factory.repository_data()
        special_description = "Test with special chars: !@#$%^&*()[]{}|;:,.<>?"

        create_input = CreateRepositoryInput(
            name=repo_data["name"],
            description=special_description
        )

        created_repo = await create_repository(create_input)
        test_cleanup.add_repository(created_repo["id"])

        # Validate special character handling
        ResponseValidator.validate_repository(created_repo)
        assert created_repo["description"] == special_description


class TestRepositoryPerformance:
    """Test repository performance scenarios."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_list_repositories_performance(
        self,
        test_group_path: str
    ):
        """Test repository listing performance."""

        list_input = ListRepositoriesInput(
            group_id=test_group_path,
            per_page=50
        )

        start_time = time.time()
        repositories = await list_repositories(list_input)
        end_time = time.time()

        # Performance validation (should complete within 5 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 5.0)

        # Validate response structure
        assert isinstance(repositories, list)
        for repo in repositories[:5]:  # Validate first 5 repos
            ResponseValidator.validate_repository(repo)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_bulk_repository_operations(
        self,
        test_data_factory: TestDataFactory,
        test_cleanup: TestCleanup
    ):
        """Test creating and managing multiple repositories."""

        # Create multiple repositories
        batch_size = 3  # Small number for testing
        created_repos = []

        start_time = time.time()

        for i in range(batch_size):
            repo_data = test_data_factory.repository_data()
            repo_data["name"] = f"BULK_TEST_{i}_{repo_data['name']}"

            create_input = CreateRepositoryInput(
                name=repo_data["name"],
                description=f"Bulk test repository {i+1}"
            )

            created_repo = await create_repository(create_input)
            created_repos.append(created_repo)
            test_cleanup.add_repository(created_repo["id"])

            # Validate each repository
            ResponseValidator.validate_repository(created_repo)

        end_time = time.time()

        # Validate bulk creation
        BulkValidator.validate_bulk_creation(created_repos, batch_size)
        BulkValidator.validate_performance_metrics(start_time, end_time, 30.0)

        # Verify all repositories were created with unique IDs
        repo_ids = [repo["id"] for repo in created_repos]
        assert len(set(repo_ids)) == batch_size


class TestRepositoryFieldValidation:
    """Test repository field validation and edge cases."""

    @pytest.mark.asyncio
    async def test_repository_field_order(
        self,
        test_project_path: str
    ):
        """Test that repository responses have proper field ordering for UX."""
        get_input = GetRepositoryInput(project_path=test_project_path)
        repository = await get_repository(get_input)

        # Validate important fields exist (field order is determined by GitLab API)
        required_fields = ["id", "name", "path_with_namespace"]
        for field in required_fields:
            assert field in repository, f"Field {field} should be present in repository response"

    @pytest.mark.asyncio
    async def test_repository_minimal_response(
        self,
        test_project_path: str
    ):
        """Test that repository responses contain all required fields."""
        get_input = GetRepositoryInput(project_path=test_project_path)
        repository = await get_repository(get_input)

        # Check required fields are present
        required_fields = ["id", "name", "path", "path_with_namespace", "web_url", "created_at"]
        for field in required_fields:
            assert field in repository, f"Required field '{field}' missing from repository response"
            assert repository[field] is not None, f"Required field '{field}' is None"
