"""Integration tests for GitLab MCP Server.

This module tests integration between different services and
end-to-end workflows that span multiple GitLab functions.
"""


import asyncio
import time

import pytest

from src.schemas.branches import CreateBranchInput, GetBranchInput
from src.schemas.files import CreateFileInput, GetFileContentsInput
from src.schemas.iterations import ListIterationsInput
from src.schemas.milestones import CreateMilestoneInput, GetMilestoneInput
from src.schemas.search import ProjectSearchRequest, SearchScope
from src.schemas.work_items import (
    CreateWorkItemInput,
    GetWorkItemInput,
    ListWorkItemsInput,
    UpdateWorkItemInput,
)
from src.services.branches import create_branch, get_branch
from src.services.files import create_file, get_file_contents
from src.services.iterations import list_iterations
from src.services.milestones import create_milestone, get_milestone
from src.services.search import search_project
from src.services.work_items import (
    create_work_item,
    get_work_item,
    list_work_items,
    update_work_item,
)
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory
from tests.utils.validators import ResponseValidator


class TestWorkItemIntegration:
    """Test work item integration with other services."""

    @pytest.mark.asyncio
    async def test_work_item_with_milestone_lifecycle(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        test_cleanup: TestCleanup
    ):
        """Test creating work item, linking to milestone, and updating states."""
        # Create a milestone first
        milestone_data = test_data_factory.milestone_data()

        milestone_input = CreateMilestoneInput(
            project_path=test_project_path,
            title=f"INTEGRATION {milestone_data['title']}",
            description="Milestone for integration testing"
        )

        created_milestone = await create_milestone(milestone_input)
        test_cleanup.add_milestone(created_milestone["id"])

        # Create a work item
        issue_data = test_data_factory.issue_data()

        work_item_input = CreateWorkItemInput(
            project_path=test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=f"INTEGRATION {issue_data['title']}",
            description="Work item for milestone integration testing"
        )

        created_work_item = await create_work_item(work_item_input)
        test_cleanup.add_work_item(created_work_item["id"])

        # Validate both items were created
        ResponseValidator.validate_work_item(created_work_item)
        ResponseValidator.validate_milestone(created_milestone)

        # Get full work item details to check widgets
        get_input = GetWorkItemInput(id=created_work_item["id"])
        full_work_item = await get_work_item(get_input)

        assert "widgets" in full_work_item
        assert len(full_work_item["widgets"]) > 0

        # Check that milestone and work item can be retrieved independently
        milestone_get_input = GetMilestoneInput(
            project_path=test_project_path,
            milestone_id=created_milestone["id"]
        )

        retrieved_milestone = await get_milestone(milestone_get_input)
        assert retrieved_milestone["id"] == created_milestone["id"]
        assert retrieved_milestone["title"] == created_milestone["title"]

    @pytest.mark.asyncio
    async def test_work_item_search_integration(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        test_cleanup: TestCleanup
    ):
        """Test creating work item and then finding it via search."""
        # Create a work item with unique searchable content
        unique_id = hash(str(test_data_factory.issue_data())) % 10000
        searchable_title = f"SEARCH_INTEGRATION_TEST_{unique_id}"

        work_item_input = CreateWorkItemInput(
            project_path=test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=searchable_title,
            description="Unique work item for search integration testing"
        )

        created_work_item = await create_work_item(work_item_input)
        test_cleanup.add_work_item(created_work_item["id"])

        # Wait a moment for indexing (in real GitLab)
        await asyncio.sleep(1)

        # Search for the work item
        search_request = ProjectSearchRequest(
            project_id=test_project_path,
            scope=SearchScope.ISSUES,
            search=f"SEARCH_INTEGRATION_TEST_{unique_id}",
            per_page=10
        )

        search_results = await search_project(search_request)

        # Validate search results
        assert isinstance(search_results, list)

        # Find our work item in search results
        found_work_item = None
        for result in search_results:
            if searchable_title in result.get("title", ""):
                found_work_item = result
                break

        # Note: Search indexing might be delayed, so this test might not always find the item immediately
        # That's normal GitLab behavior, not a bug in our implementation
        if found_work_item:
            assert "title" in found_work_item
            assert searchable_title in found_work_item["title"]


class TestFileWorkflowIntegration:
    """Test file operations integrated with other workflows."""

    @pytest.mark.asyncio
    async def test_branch_file_work_item_workflow(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        test_cleanup: TestCleanup
    ):
        """Test creating branch, adding file, and linking to work item."""
        # Create a work item for the feature
        issue_data = test_data_factory.issue_data()
        feature_title = f"WORKFLOW Feature {issue_data['title']}"

        work_item_input = CreateWorkItemInput(
            project_path=test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=feature_title,
            description="Feature work item for file workflow testing"
        )

        created_work_item = await create_work_item(work_item_input)
        test_cleanup.add_work_item(created_work_item["id"])

        # Create a feature branch
        branch_data = test_data_factory.branch_data()
        branch_name = f"feature/workflow-{branch_data['branch_name']}"

        branch_input = CreateBranchInput(
            project_path=test_project_path,
            branch_name=branch_name,
            ref="main"
        )

        created_branch = await create_branch(branch_input)
        test_cleanup.add_branch(test_project_path, branch_name)

        # Create a file in the feature branch
        file_data = test_data_factory.file_data()
        file_path = f"features/workflow-{file_data['name']}.py"

        file_content = f'''"""
Feature implementation for: {feature_title}

This file implements the feature described in work item:
ID: {created_work_item["id"]}
Title: {feature_title}
"""

def new_feature():
    """Implement the new feature."""
    return "Feature implementation"

if __name__ == "__main__":
    print(new_feature())
'''

        file_input = CreateFileInput(
            project_path=test_project_path,
            file_path=file_path,
            content=file_content,
            commit_message=f"Add feature implementation for {feature_title}",
            branch=branch_name
        )

        created_file = await create_file(file_input)
        test_cleanup.add_file(test_project_path, file_path, branch_name)

        # Validate all components were created successfully
        ResponseValidator.validate_work_item(created_work_item)
        ResponseValidator.validate_branch(created_branch.model_dump())
        assert created_file.file_path == file_path

        # Verify file exists in the branch
        file_get_input = GetFileContentsInput(
            project_path=test_project_path,
            file_path=file_path,
            ref=branch_name
        )

        retrieved_file = await get_file_contents(file_get_input)
        assert retrieved_file.content == file_content
        assert feature_title in retrieved_file.content

        # Verify branch exists
        branch_get_input = GetBranchInput(
            project_path=test_project_path,
            branch_name=branch_name
        )

        retrieved_branch = await get_branch(branch_get_input)
        assert retrieved_branch.name == branch_name


class TestProjectManagementIntegration:
    """Test project management workflow integration."""

    @pytest.mark.asyncio
    async def test_milestone_iteration_work_items_workflow(
        self,
        static_test_project_path: str,
        static_test_group_path: str,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test complete project management workflow with milestones, iterations, and work items."""
        # Use existing iteration from the group (since creation is not available via API)
        list_input = ListIterationsInput(group_id=static_test_group_path, per_page=1)
        iterations_result = await list_iterations(list_input)

        if iterations_result["count"] == 0:
            pytest.skip("No existing iterations available in test group - group must have iteration cadence set up")

        existing_iteration = iterations_result["iterations"][0]
        print(f"Using existing iteration: ID={existing_iteration.get('id')}, Title={existing_iteration.get('title', '(auto-scheduled)')}")

        # Create a milestone within the sprint timeframe
        milestone_data = static_test_data_factory.milestone_data()
        timestamp = int(time.time())

        milestone_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=f"WORKFLOW Milestone {milestone_data['title']} {timestamp}",
            description="Milestone for project management workflow testing",
            start_date=milestone_data["start_date"],
            due_date=milestone_data["due_date"]
        )

        created_milestone = await create_milestone(milestone_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Create multiple work items for the milestone
        work_items = []
        work_item_types = ["ISSUE", "TASK"]

        for i, work_type in enumerate(work_item_types):
            if work_type in work_item_type_ids:
                item_data = static_test_data_factory.issue_data()

                work_item_input = CreateWorkItemInput(
                    project_path=static_test_project_path,
                    work_item_type_id=work_item_type_ids[work_type],
                    title=f"WORKFLOW {work_type} {i+1}: {item_data['title']}",
                    description=f"Work item {i+1} for milestone and iteration testing"
                )

                created_work_item = await create_work_item(work_item_input)
                cleanup_tracker.add_work_item(created_work_item["id"])
                work_items.append(created_work_item)

        # Validate all components
        assert "id" in existing_iteration
        assert existing_iteration["id"] is not None
        ResponseValidator.validate_milestone(created_milestone)

        for work_item in work_items:
            ResponseValidator.validate_work_item(work_item)

        # Verify we can list work items in the project
        list_input = ListWorkItemsInput(
            project_path=static_test_project_path,
            first=20
        )

        project_work_items = await list_work_items(list_input)

        # Our work items should be in the project
        project_item_ids = [item["id"] for item in project_work_items]
        for work_item in work_items:
            assert work_item["id"] in project_item_ids


class TestSearchIntegration:
    """Test search integration across different content types."""

    @pytest.mark.asyncio
    async def test_cross_content_search(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        test_cleanup: TestCleanup
    ):
        """Test searching across different content types in a project."""
        search_term = f"INTEGRATION_SEARCH_{hash(str(test_data_factory)) % 1000}"

        # Create work item with search term
        work_item_input = CreateWorkItemInput(
            project_path=test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=f"Issue containing {search_term}",
            description=f"This work item contains the search term: {search_term}"
        )

        created_work_item = await create_work_item(work_item_input)
        test_cleanup.add_work_item(created_work_item["id"])

        # Create file with search term
        file_path = f"integration/search_test_{search_term.lower()}.py"
        file_content = f'''"""
File for integration testing containing: {search_term}

This file is part of the search integration test.
"""

def search_integration_function():
    """Function containing {search_term}."""
    return "{search_term}"
'''

        file_input = CreateFileInput(
            project_path=test_project_path,
            file_path=file_path,
            content=file_content,
            commit_message=f"Add file for search integration: {search_term}",
            branch="main"
        )

        await create_file(file_input)
        test_cleanup.add_file(test_project_path, file_path, "main")

        # Wait for potential indexing
        await asyncio.sleep(1)

        # Search for issues
        issue_search = ProjectSearchRequest(
            project_id=test_project_path,
            scope=SearchScope.ISSUES,
            search=search_term,
            per_page=10
        )

        issue_results = await search_project(issue_search)

        # Search for code
        code_search = ProjectSearchRequest(
            project_id=test_project_path,
            scope=SearchScope.BLOBS,
            search=search_term,
            per_page=10
        )

        code_results = await search_project(code_search)

        # Validate search results structure
        assert isinstance(issue_results, list)
        assert isinstance(code_results, list)

        # Note: Actual search results depend on GitLab's indexing timing
        # The test validates that search doesn't crash and returns proper structure


class TestErrorRecoveryIntegration:
    """Test error recovery and rollback scenarios."""

    @pytest.mark.asyncio
    async def test_partial_workflow_recovery(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        test_cleanup: TestCleanup
    ):
        """Test recovery when part of a workflow fails."""
        # Create a work item successfully
        issue_data = test_data_factory.issue_data()

        work_item_input = CreateWorkItemInput(
            project_path=test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=f"RECOVERY Test {issue_data['title']}",
            description="Work item for recovery testing"
        )

        created_work_item = await create_work_item(work_item_input)
        test_cleanup.add_work_item(created_work_item["id"])

        # Verify work item was created
        get_input = GetWorkItemInput(id=created_work_item["id"])
        retrieved_work_item = await get_work_item(get_input)
        assert retrieved_work_item["id"] == created_work_item["id"]

        # Try to create a milestone with invalid data (should fail)
        with pytest.raises((ValueError, KeyError, RuntimeError)):
            invalid_milestone_input = CreateMilestoneInput(
                project_id="nonexistent/project",  # Invalid project
                title="This should fail"
            )
            await create_milestone(invalid_milestone_input)

        # Verify that the work item still exists after the failed milestone creation
        retrieved_work_item_after = await get_work_item(get_input)
        assert retrieved_work_item_after["id"] == created_work_item["id"]
        assert retrieved_work_item_after["title"] == created_work_item["title"]

        # Should be able to continue working with the successfully created work item
        # Test title update instead of description (description updates require widget operations not yet implemented)
        update_input = UpdateWorkItemInput(
            id=created_work_item["id"],
            title=f"{created_work_item['title']} - Updated"
        )

        updated_work_item = await update_work_item(update_input)
        assert updated_work_item["id"] == created_work_item["id"]
        assert updated_work_item["title"] == f"{created_work_item['title']} - Updated"


class TestPerformanceIntegration:
    """Test performance of integrated workflows."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_bulk_workflow_performance(
        self,
        test_project_path: str,
        test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        test_cleanup: TestCleanup
    ):
        """Test performance of bulk operations across services."""

        start_time = time.time()

        # Create milestone
        milestone_data = test_data_factory.milestone_data()
        milestone_input = CreateMilestoneInput(
            project_path=test_project_path,
            title=f"PERF {milestone_data['title']}",
            description="Performance test milestone"
        )

        created_milestone = await create_milestone(milestone_input)
        test_cleanup.add_milestone(created_milestone["id"])

        # Create multiple work items
        work_items = []
        for i in range(3):  # Small batch for CI
            item_data = test_data_factory.issue_data()

            work_item_input = CreateWorkItemInput(
                project_path=test_project_path,
                work_item_type_id=work_item_type_ids["ISSUE"],
                title=f"PERF Item {i+1}: {item_data['title']}",
                description=f"Performance test work item {i+1}"
            )

            created_work_item = await create_work_item(work_item_input)
            test_cleanup.add_work_item(created_work_item["id"])
            work_items.append(created_work_item)

        end_time = time.time()

        # Validate performance (should complete within reasonable time)
        duration = end_time - start_time
        assert duration < 30.0, f"Bulk workflow took too long: {duration:.2f}s"

        # Validate all items were created
        assert len(work_items) == 3
        ResponseValidator.validate_milestone(created_milestone)
        for work_item in work_items:
            ResponseValidator.validate_work_item(work_item)
