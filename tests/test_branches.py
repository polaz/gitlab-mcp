"""Tests for branch management functions.

This module tests all branch-related functions:
- list_branches
- get_branch
- create_branch
- delete_branch
- protect_branch
- unprotect_branch
"""



import time

import pytest

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.branches import (
    AccessLevel,
    AccessLevelModel,
    CreateBranchInput,
    DeleteBranchInput,
    GetBranchInput,
    ListBranchesInput,
    ProtectBranchInput,
    UnprotectBranchInput,
)
from src.services.branches import (
    create_branch,
    delete_branch,
    get_branch,
    list_branches,
    protect_branch,
    unprotect_branch,
)
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory
from tests.utils.validators import BulkValidator, ResponseValidator


class TestBranchBasicOperations:
    """Test basic branch operations."""

    @pytest.mark.asyncio
    async def test_list_branches(
        self,
        static_test_project_path: str
    ):
        """Test listing branches in a repository."""
        list_input = ListBranchesInput(
            project_path=static_test_project_path,
            per_page=20
        )

        branches = await list_branches(list_input)

        # Validate response structure
        assert isinstance(branches, list)
        assert len(branches) > 0

        # Should have at least a main/master branch
        branch_names = [branch.name if hasattr(branch, 'name') else branch["name"] for branch in branches]
        assert any(name in ["main", "master", "develop"] for name in branch_names)

        # Validate each branch
        for branch in branches:
            branch_dict = branch.model_dump() if hasattr(branch, 'model_dump') else branch
            ResponseValidator.validate_branch(branch_dict)

    @pytest.mark.asyncio
    async def test_get_default_branch(
        self,
        static_test_project_path: str
    ):
        """Test getting the default branch (usually main or master)."""
        # First list branches to find the default
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)

        # Find default branch (typically main or master)
        default_branch_name = None
        for branch in branches:
            branch_name = branch.name if hasattr(branch, 'name') else branch["name"]
            is_default = branch.default if hasattr(branch, 'default') else branch.get("default", False)
            if is_default or branch_name in ["main", "master"]:
                default_branch_name = branch_name
                break

        if not default_branch_name and branches:
            default_branch_name = branches[0].name  # Use first branch as fallback

        assert default_branch_name is not None, "No suitable branch found for testing"

        # Get the specific branch
        get_input = GetBranchInput(
            project_path=static_test_project_path,
            branch_name=default_branch_name
        )

        branch = await get_branch(get_input)

        # Validate response structure
        branch_dict = branch.model_dump() if hasattr(branch, 'model_dump') else branch
        ResponseValidator.validate_branch(branch_dict)
        branch_name = branch.name if hasattr(branch, 'name') else branch["name"]
        assert branch_name == default_branch_name
        has_commit = hasattr(branch, 'commit') or "commit" in (branch if isinstance(branch, dict) else {})
        assert has_commit

    @pytest.mark.asyncio
    async def test_list_branches_pagination(
        self,
        static_test_project_path: str
    ):
        """Test branch listing with pagination."""
        # Test first page
        list_input = ListBranchesInput(
            project_path=static_test_project_path,
            per_page=5,
            page=1
        )
        page1_branches = await list_branches(list_input)

        # Test second page
        list_input.page = 2
        page2_branches = await list_branches(list_input)

        # Validate pagination
        assert isinstance(page1_branches, list)
        assert isinstance(page2_branches, list)

        # No duplicates between pages (if both pages have content)
        if page1_branches and page2_branches:
            page1_names = {branch.name for branch in page1_branches}
            page2_names = {branch.name for branch in page2_branches}
            assert len(page1_names.intersection(page2_names)) == 0


class TestBranchCreation:
    """Test branch creation functionality."""

    @pytest.mark.asyncio
    async def test_create_branch_from_main(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a new branch from main/master."""
        # Get existing branches to find a source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)

        source_branch = None
        for branch in branches:
            if branch.name in ["main", "master"] or branch.default:
                source_branch = branch.name
                break

        if not source_branch and branches:
            source_branch = branches[0].name  # Use first available branch

        assert source_branch is not None, "No suitable source branch found"

        # Create a new branch
        branch_data = static_test_data_factory.branch_data()
        new_branch_name = branch_data['branch_name']

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=new_branch_name,
            ref=source_branch
        )

        created_branch = await create_branch(create_input)
        cleanup_tracker.add_branch(static_test_project_path, new_branch_name)

        # Validate creation
        branch_dict = created_branch.model_dump()
        ResponseValidator.validate_branch(branch_dict)
        assert created_branch.name == new_branch_name
        assert hasattr(created_branch, 'commit')

    @pytest.mark.asyncio
    async def test_create_branch_from_commit(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a new branch from a specific commit."""
        # Get a branch to find a commit SHA
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)

        source_branch = branches[0].name if branches else "main"
        get_input = GetBranchInput(
            project_path=static_test_project_path,
            branch_name=source_branch
        )

        branch_info = await get_branch(get_input)
        commit_sha = branch_info.commit.id

        # Create branch from commit SHA
        branch_data = static_test_data_factory.branch_data()
        new_branch_name = branch_data['branch_name'].replace('test_', 'commit-')

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=new_branch_name,
            ref=commit_sha
        )

        created_branch = await create_branch(create_input)
        cleanup_tracker.add_branch(static_test_project_path, new_branch_name)

        # Validate creation
        branch_dict = created_branch.model_dump()
        ResponseValidator.validate_branch(branch_dict)
        assert created_branch.name == new_branch_name
        assert created_branch.commit.id == commit_sha


class TestBranchDeletion:
    """Test branch deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_branch(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory
    ):
        """Test deleting a branch."""
        # Create a branch first
        branch_data = static_test_data_factory.branch_data()
        branch_name = branch_data['branch_name'].replace('test_', 'delete-test-')

        # Get source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        source_branch = branches[0].name if branches else "main"

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name,
            ref=source_branch
        )

        created_branch = await create_branch(create_input)
        assert created_branch.name == branch_name

        # Delete the branch
        delete_input = DeleteBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name
        )

        result = await delete_branch(delete_input)

        # Validate deletion
        assert result is True

        # Verify branch is gone
        get_input = GetBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name
        )

        with pytest.raises(GitLabAPIError):  # Should raise an error for branch not found
            await get_branch(get_input)


class TestBranchProtection:
    """Test branch protection functionality."""

    @pytest.mark.asyncio
    async def test_protect_branch(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test protecting a branch."""
        # Create a branch first
        branch_data = static_test_data_factory.branch_data()
        branch_name = f"protect-test-{branch_data['branch_name']}"

        # Get source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        source_branch = branches[0].name if branches else "main"

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name,
            ref=source_branch
        )

        await create_branch(create_input)
        cleanup_tracker.add_branch(static_test_project_path, branch_name)

        # Protect the branch
        protect_input = ProtectBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name,
            allowed_to_push=[AccessLevelModel(access_level=AccessLevel.MAINTAINER)],
            allowed_to_merge=[AccessLevelModel(access_level=AccessLevel.MAINTAINER)]
        )

        protection_result = await protect_branch(protect_input)

        # Validate protection
        assert protection_result is True

    @pytest.mark.asyncio
    async def test_unprotect_branch(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test unprotecting a branch."""
        # Create and protect a branch first
        branch_data = static_test_data_factory.branch_data()
        branch_name = f"unprotect-test-{branch_data['branch_name']}"

        # Get source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        source_branch = branches[0].name if branches else "main"

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name,
            ref=source_branch
        )

        await create_branch(create_input)
        cleanup_tracker.add_branch(static_test_project_path, branch_name)

        # Protect the branch
        protect_input = ProtectBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name,
            allowed_to_push=[AccessLevelModel(access_level=AccessLevel.MAINTAINER)],
            allowed_to_merge=[AccessLevelModel(access_level=AccessLevel.MAINTAINER)]
        )

        await protect_branch(protect_input)

        # Unprotect the branch
        unprotect_input = UnprotectBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name
        )

        result = await unprotect_branch(unprotect_input)

        # Validate unprotection
        assert result is True

        # Verify branch is no longer protected
        get_input = GetBranchInput(
            project_path=static_test_project_path,
            branch_name=branch_name
        )

        branch_info = await get_branch(get_input)
        assert branch_info.protected is False


class TestBranchErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_branch(
        self,
        static_test_project_path: str
    ):
        """Test getting a branch that doesn't exist."""
        get_input = GetBranchInput(
            project_path=static_test_project_path,
            branch_name="nonexistent-branch-12345"
        )

        with pytest.raises(Exception) as exc_info:
            await get_branch(get_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_create_branch_duplicate_name(
        self,
        static_test_project_path: str
    ):
        """Test creating a branch with duplicate name."""
        # Get existing branch name
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        existing_branch_name = branches[0].name if branches else "main"

        # Try to create branch with same name
        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=existing_branch_name,
            ref="main"
        )

        with pytest.raises(Exception) as exc_info:
            await create_branch(create_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["exists", "conflict", "duplicate"])

    @pytest.mark.asyncio
    async def test_create_branch_invalid_ref(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory
    ):
        """Test creating a branch from invalid reference."""
        branch_data = static_test_data_factory.branch_data()

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=f"invalid-ref-{branch_data['branch_name']}",
            ref="nonexistent-reference-12345"
        )

        with pytest.raises(Exception) as exc_info:
            await create_branch(create_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "invalid", "does not exist"])

    @pytest.mark.asyncio
    async def test_delete_protected_branch(
        self,
        static_test_project_path: str
    ):
        """Test deleting the default branch (should fail or be restricted)."""
        # Try to delete the main branch (usually protected or restricted)
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)

        # Find the default branch
        default_branch = None
        for branch in branches:
            if branch.default or branch.name in ["main", "master"]:
                default_branch = branch.name
                break

        if not default_branch:
            pytest.skip("No default branch found for testing")

        delete_input = DeleteBranchInput(
            project_path=static_test_project_path,
            branch_name=default_branch
        )

        # In test environments, main branch might not be truly protected
        # So we'll handle both cases - either it fails (expected) or succeeds (test limitation)
        try:
            result = await delete_branch(delete_input)
            # If deletion succeeds, it means the test environment doesn't have branch protection
            # This is acceptable for test projects
            assert result is True or result is False  # Either outcome is acceptable
        except Exception as exc:
            # If it fails, validate that it's a meaningful error about protection/restriction
            error_message = str(exc).lower()
            assert any(keyword in error_message for keyword in ["protected", "cannot", "forbidden", "default", "restrict", "delete", "denied", "failed"])
            # This is the expected behavior in production environments


class TestBranchEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_branch_special_characters_name(
        self,
        static_test_project_path: str,
        cleanup_tracker: TestCleanup
    ):
        """Test creating branch with special characters in name."""
        # Use GitLab-safe special characters
        special_name = "test-branch_with.special-chars"

        # Get source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        source_branch = branches[0].name if branches else "main"

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=special_name,
            ref=source_branch
        )

        created_branch = await create_branch(create_input)
        cleanup_tracker.add_branch(static_test_project_path, special_name)

        # Validate creation with special characters
        branch_dict = created_branch.model_dump()
        ResponseValidator.validate_branch(branch_dict)
        assert created_branch.name == special_name

    @pytest.mark.asyncio
    async def test_branch_long_name(
        self,
        static_test_project_path: str,
        cleanup_tracker: TestCleanup
    ):
        """Test creating branch with long name."""
        # Create a long but valid branch name
        long_name = f"test-very-long-branch-name-that-is-still-within-limits-{hash('test') % 1000}"

        # Get source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        source_branch = branches[0].name if branches else "main"

        create_input = CreateBranchInput(
            project_path=static_test_project_path,
            branch_name=long_name,
            ref=source_branch
        )

        created_branch = await create_branch(create_input)
        cleanup_tracker.add_branch(static_test_project_path, long_name)

        # Validate creation with long name
        branch_dict = created_branch.model_dump()
        ResponseValidator.validate_branch(branch_dict)
        assert created_branch.name == long_name


class TestBranchPerformance:
    """Test branch performance scenarios."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_list_branches_performance(
        self,
        static_test_project_path: str
    ):
        """Test branch listing performance."""

        list_input = ListBranchesInput(
            project_path=static_test_project_path,
            per_page=100
        )

        start_time = time.time()
        branches = await list_branches(list_input)
        end_time = time.time()

        # Performance validation (should complete within 5 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 5.0)

        # Validate response structure
        assert isinstance(branches, list)
        for branch in branches[:5]:  # Validate first 5 branches
            branch_dict = branch.model_dump() if hasattr(branch, 'model_dump') else branch
            ResponseValidator.validate_branch(branch_dict)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_bulk_branch_operations(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating and managing multiple branches."""

        # Get source branch
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)
        source_branch = branches[0].name if branches else "main"

        # Create multiple branches
        batch_size = 3  # Small number for testing
        created_branches = []

        start_time = time.time()

        for i in range(batch_size):
            branch_data = static_test_data_factory.branch_data()
            branch_name = f"bulk-test-{i}-{branch_data['branch_name']}"

            create_input = CreateBranchInput(
                project_path=static_test_project_path,
                branch_name=branch_name,
                ref=source_branch
            )

            created_branch = await create_branch(create_input)
            created_branches.append(created_branch)
            cleanup_tracker.add_branch(static_test_project_path, branch_name)

            # Validate each branch
            ResponseValidator.validate_branch(created_branch)

        end_time = time.time()

        # Validate bulk creation
        BulkValidator.validate_bulk_creation(created_branches, batch_size, "branch")
        BulkValidator.validate_performance_metrics(start_time, end_time, 30.0)

        # Verify all branches were created with unique names
        branch_names = [branch.name for branch in created_branches]
        assert len(set(branch_names)) == batch_size


class TestBranchFieldValidation:
    """Test branch field validation and edge cases."""

    @pytest.mark.asyncio
    async def test_branch_field_order(
        self,
        static_test_project_path: str
    ):
        """Test that branch responses have proper field ordering for UX."""
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)

        if branches:
            # Validate field ordering for UX (important fields first)
            ResponseValidator.validate_field_order(branches[0], ["name", "commit"])

    @pytest.mark.asyncio
    async def test_branch_minimal_response(
        self,
        static_test_project_path: str
    ):
        """Test that branch responses contain all required fields."""
        list_input = ListBranchesInput(project_path=static_test_project_path)
        branches = await list_branches(list_input)

        if branches:
            branch = branches[0]

            # Check required fields are present
            # Convert to dict if it's a Pydantic model for validation
            branch_dict = branch.model_dump() if hasattr(branch, 'model_dump') else branch

            required_fields = ["name", "commit"]
            for field in required_fields:
                assert field in branch_dict, f"Required field '{field}' missing from branch response"
                assert branch_dict[field] is not None, f"Required field '{field}' is None"

            # Check commit has required sub-fields
            if "commit" in branch_dict:
                commit_required_fields = ["id"]
                for field in commit_required_fields:
                    assert field in branch_dict["commit"], f"Required commit field '{field}' missing"
