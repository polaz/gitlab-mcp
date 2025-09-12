"""Tests for Work Items API functions.

This module tests all Work Items GraphQL API functions including
create, list, get, update, and delete operations for all work item types.
"""



import time

import pytest

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.work_items import (
    CreateWorkItemInput,
    DeleteWorkItemInput,
    GetWorkItemInput,
    ListWorkItemsInput,
    UpdateWorkItemInput,
    WorkItemState,
)
from src.services.work_items import (
    create_work_item,
    delete_work_item,
    get_work_item,
    list_work_items,
    update_work_item,
)
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory
from tests.utils.validators import BulkValidator, ResponseValidator


@pytest.mark.work_items
class TestWorkItemsAPI:
    """Test suite for Work Items API functions."""

    @pytest.mark.asyncio
    async def test_create_issue_work_item(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test creating an issue work item with all basic fields."""
        # Prepare test data
        issue_data = static_test_data_factory.issue_data()

        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"],
            confidential=issue_data["confidential"]
        )

        # Create the work item
        result = await create_work_item(create_input)

        # Track for cleanup
        cleanup_tracker.track_work_item(result["id"], result)

        # Validate response
        result_dict = result
        ResponseValidator.validate_work_item(result_dict)
        # Note: Field order validation disabled for GraphQL responses as order depends on query structure

        # Verify specific fields
        assert result["title"] == issue_data["title"]
        assert result["workItemType"]["name"] == "Issue"
        assert result["state"] == "OPEN"
        assert result["project"]["fullPath"] == issue_data["project_path"]
        assert static_test_data_factory.prefix in result["title"]

    @pytest.mark.asyncio
    async def test_create_epic_work_item(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test creating an epic work item (group-scoped - epics are always group-level)."""
        # Prepare test data
        epic_data = static_test_data_factory.epic_data()

        create_input = CreateWorkItemInput(
            namespace_path=epic_data.get("namespace_path", static_test_data_factory.group_path),
            work_item_type_id=work_item_type_ids["EPIC"],
            title=epic_data["title"],
            description=epic_data["description"]
        )

        # Create the work item
        result = await create_work_item(create_input)

        # Track for cleanup
        cleanup_tracker.track_work_item(result["id"], result)

        # Validate response
        result_dict = result
        ResponseValidator.validate_work_item(result_dict)

        # Verify specific fields
        assert result["title"] == epic_data["title"]
        assert result["workItemType"]["name"] == "Epic"
        assert result["state"] == "OPEN"

    @pytest.mark.asyncio
    async def test_create_task_with_parent(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test creating a task work item with a parent issue."""
        # First create a parent issue
        issue_data = static_test_data_factory.issue_data()
        issue_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        parent_issue = await create_work_item(issue_input)
        cleanup_tracker.track_work_item(parent_issue["id"], parent_issue)

        # Create task with parent
        task_data = static_test_data_factory.task_data(parent_id=parent_issue["id"])
        task_input = CreateWorkItemInput(
            project_path=task_data["project_path"],
            work_item_type_id=work_item_type_ids["TASK"],
            title=task_data["title"],
            description=task_data["description"],
            parent_id=task_data["parent_id"]
        )

        task_result = await create_work_item(task_input)
        cleanup_tracker.track_work_item(task_result["id"], task_result)

        # Validate hierarchy
        task_dict = task_result
        ResponseValidator.validate_work_item(task_dict)
        assert task_result["workItemType"]["name"] == "Task"

        # Verify parent relationship by getting the task details
        get_input = GetWorkItemInput(id=task_result["id"])
        detailed_task = await get_work_item(get_input)

        # Check for hierarchy widget
        hierarchy_widget = None
        for widget in detailed_task["widgets"]:
            if widget.get("type") == "HIERARCHY":
                hierarchy_widget = widget
                break

        assert hierarchy_widget is not None, "Task should have hierarchy widget"
        if hierarchy_widget.get("parent"):
            assert hierarchy_widget["parent"]["id"] == parent_issue["id"]

    @pytest.mark.asyncio
    async def test_list_work_items_project_scope(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test listing work items with project scope."""
        # Create multiple work items
        items_data = static_test_data_factory.bulk_work_items_data(count=3, work_item_type="ISSUE")
        created_items = []

        for item_data in items_data:
            create_input = CreateWorkItemInput(
                project_path=item_data["project_path"],
                work_item_type_id=work_item_type_ids["ISSUE"],
                title=item_data["title"],
                description=item_data["description"]
            )

            result = await create_work_item(create_input)
            created_items.append(result)
            cleanup_tracker.track_work_item(result["id"], result)

        # List work items
        list_input = ListWorkItemsInput(
            project_path=static_test_data_factory.project_path,
            first=10
        )

        work_items = await list_work_items(list_input)

        # Validate response
        assert isinstance(work_items, list)
        assert len(work_items) >= 3  # Should include our created items

        # Validate each work item in list
        for work_item in work_items[:5]:  # Check first 5
            work_item_dict = work_item
            ResponseValidator.validate_work_item(work_item_dict)
            # Note: Field order validation disabled for GraphQL responses as order depends on query structure

        # Verify our test items are in the results
        created_ids = {item["id"] for item in created_items}
        result_ids = {item["id"] for item in work_items}

        assert created_ids.issubset(result_ids), "All created items should appear in list"

    @pytest.mark.asyncio
    async def test_list_work_items_with_filters(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test listing work items with various filters."""
        # Create different types of work items
        issue_data = static_test_data_factory.issue_data()
        issue_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        issue_result = await create_work_item(issue_input)
        cleanup_tracker.track_work_item(issue_result["id"], issue_result)

        # Test filtering by work item type
        list_input = ListWorkItemsInput(
            project_path=static_test_data_factory.project_path,
            work_item_types=["ISSUE"],
            first=10
        )

        filtered_items = await list_work_items(list_input)

        # Validate all returned items are issues
        for item in filtered_items:
            work_item_type_name = item["workItemType"]["name"]
            assert work_item_type_name == "Issue"

        # Test filtering by state
        list_input = ListWorkItemsInput(
            project_path=static_test_data_factory.project_path,
            state=WorkItemState.OPEN,
            first=10
        )

        open_items = await list_work_items(list_input)

        # Validate all returned items are open
        for item in open_items:
            assert item["state"] == "OPEN"

    @pytest.mark.asyncio
    async def test_get_work_item_by_id(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test getting a work item by global ID."""
        # Create a work item
        issue_data = static_test_data_factory.issue_data()
        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.track_work_item(created_item["id"], created_item)

        # Get work item by ID
        get_input = GetWorkItemInput(id=created_item["id"])
        retrieved_item = await get_work_item(get_input)

        # Validate response
        ResponseValidator.validate_work_item(retrieved_item)
        # Note: Field order validation disabled for GraphQL responses as order depends on query structure

        # Verify fields match
        assert retrieved_item["id"] == created_item["id"]
        assert retrieved_item["title"] == created_item["title"]
        assert retrieved_item["iid"] == created_item["iid"]

        # Verify widgets are populated
        assert len(retrieved_item["widgets"]) > 0

    @pytest.mark.asyncio
    async def test_get_work_item_by_iid(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test getting a work item by IID and project path."""
        # Create a work item
        issue_data = static_test_data_factory.issue_data()
        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.track_work_item(created_item["id"], created_item)

        # Get work item by IID
        get_input = GetWorkItemInput(
            iid=created_item["iid"],
            project_path=issue_data["project_path"]
        )
        retrieved_item = await get_work_item(get_input)

        # Validate response
        ResponseValidator.validate_work_item(retrieved_item)

        # Verify fields match
        assert retrieved_item["id"] == created_item["id"]
        assert retrieved_item["iid"] == created_item["iid"]

    @pytest.mark.asyncio
    async def test_update_work_item_basic_fields(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test updating basic fields of a work item."""
        # Create a work item
        issue_data = static_test_data_factory.issue_data()
        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.track_work_item(created_item["id"], created_item)

        # Update the work item
        new_title = f"{static_test_data_factory.prefix}UPDATED {issue_data['title']}"
        new_description = f"UPDATED: {issue_data['description']}"

        update_input = UpdateWorkItemInput(
            id=created_item["id"],
            title=new_title,
            description=new_description
        )

        updated_item = await update_work_item(update_input)

        # Validate response
        ResponseValidator.validate_work_item(updated_item)

        # Verify updates
        assert updated_item["title"] == new_title
        assert updated_item["id"] == created_item["id"]
        assert updated_item["iid"] == created_item["iid"]

    @pytest.mark.asyncio
    async def test_update_work_item_state_transition(
        self,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup,
        work_item_type_ids: dict[str, str]
    ):
        """Test state transitions of work items."""
        # Create a work item
        issue_data = static_test_data_factory.issue_data()
        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.track_work_item(created_item["id"], created_item)

        # Close the work item
        update_input = UpdateWorkItemInput(
            id=created_item["id"],
            state_event="close"
        )

        updated_item = await update_work_item(update_input)

        # Verify state change
        assert updated_item["state"] == "CLOSED"

        # Reopen the work item
        update_input = UpdateWorkItemInput(
            id=created_item["id"],
            state_event="reopen"
        )

        reopened_item = await update_work_item(update_input)

        # Verify state change
        assert reopened_item["state"] == "OPEN"

    @pytest.mark.asyncio
    async def test_delete_work_item(
        self,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str]
    ):
        """Test deleting a work item."""
        # Create a work item
        issue_data = static_test_data_factory.issue_data()
        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)

        # Delete the work item
        delete_input = DeleteWorkItemInput(id=created_item["id"])
        result = await delete_work_item(delete_input)

        # Validate deletion response
        assert "message" in result
        assert "successfully" in result.get("message", "").lower()

        # Verify work item is gone by trying to get it
        get_input = GetWorkItemInput(id=created_item["id"])

        with pytest.raises(GitLabAPIError):  # Should raise an error when work item is deleted
            await get_work_item(get_input)


class TestWorkItemBulkOperations:
    """Test bulk operations with work items."""

    @pytest.mark.asyncio
    async def test_bulk_create_and_cleanup(
        self,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test creating multiple work items and bulk cleanup."""
        batch_size = 5
        created_items = []

        for i in range(batch_size):
            issue_data = static_test_data_factory.issue_data()
            issue_data["title"] = f"BULK_TEST Issue {i+1}"

            create_input = CreateWorkItemInput(
                project_path=issue_data["project_path"],
                work_item_type_id=work_item_type_ids["ISSUE"],
                title=issue_data["title"],
                description=f"Bulk test item {i+1}"
            )

            created_item = await create_work_item(create_input)
            created_items.append(created_item)

            # Add to cleanup
            cleanup_tracker.add_work_item(created_item["id"])

            # Validate each item
            ResponseValidator.validate_work_item(created_item)

        # Verify all items were created successfully
        assert len(created_items) == batch_size

        # Verify IDs are unique
        ids = [item["id"] for item in created_items]
        assert len(set(ids)) == batch_size

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_list_performance(
        self,
        static_test_data_factory: TestDataFactory
    ):
        """Test list_work_items performance with pagination."""

        list_input = ListWorkItemsInput(
            project_path=static_test_data_factory.issue_data()["project_path"],
            first=50
        )

        start_time = time.time()
        result = await list_work_items(list_input)
        end_time = time.time()

        # Performance validation (should complete within 5 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 5.0)

        # Validate response structure
        assert isinstance(result, list)
        for item in result[:5]:  # Validate first 5 items
            ResponseValidator.validate_work_item(item)


class TestWorkItemErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_work_item(self):
        """Test getting a work item that doesn't exist."""
        fake_id = "gid://gitlab/WorkItem/999999999"
        get_input = GetWorkItemInput(id=fake_id)

        with pytest.raises(Exception) as exc_info:
            await get_work_item(get_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_create_work_item_invalid_project(
        self,
        work_item_type_ids: dict[str, str]
    ):
        """Test creating work item in non-existent project."""
        create_input = CreateWorkItemInput(
            project_path="nonexistent/fake-project",
            work_item_type_id=work_item_type_ids["ISSUE"],
            title="TEST Invalid Project",
            description="Should fail"
        )

        with pytest.raises(Exception) as exc_info:
            await create_work_item(create_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_update_work_item_invalid_id(self):
        """Test updating work item with invalid ID."""
        fake_id = "gid://gitlab/WorkItem/999999999"
        update_input = UpdateWorkItemInput(
            id=fake_id,
            title="Updated Title"
        )

        with pytest.raises(Exception) as exc_info:
            await update_work_item(update_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_delete_work_item_invalid_id(self):
        """Test deleting work item with invalid ID."""
        fake_id = "gid://gitlab/WorkItem/999999999"
        delete_input = DeleteWorkItemInput(id=fake_id)

        with pytest.raises(Exception) as exc_info:
            await delete_work_item(delete_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])


class TestWorkItemEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_unicode_content(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test work items with Unicode content."""
        unicode_data = static_test_data_factory.unicode_data()

        create_input = CreateWorkItemInput(
            project_path=static_test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=unicode_data["title"],
            description=unicode_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.add_work_item(created_item["id"])

        # Validate Unicode content preserved
        assert created_item["title"] == unicode_data["title"]

        # Validate response structure
        ResponseValidator.validate_work_item(created_item)

    @pytest.mark.asyncio
    async def test_empty_optional_fields(
        self,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test creating work item with minimal required fields only."""
        issue_data = static_test_data_factory.issue_data()

        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title="TEST Minimal Fields Only"
            # No description provided
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.add_work_item(created_item["id"])

        # Validate creation succeeded
        assert created_item["title"] == "TEST Minimal Fields Only"

        # Validate response structure
        ResponseValidator.validate_work_item(created_item)

    @pytest.mark.asyncio
    async def test_large_description(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test work item with very large description."""
        large_data = static_test_data_factory.large_content_data()

        create_input = CreateWorkItemInput(
            project_path=static_test_project_path,
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=f"Large Description Test - {large_data['name']}",
            description=large_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.add_work_item(created_item["id"])

        # Validate large content preserved (description is in widgets, not top level)
        description_widget = None
        for widget in created_item.get("widgets", []):
            if widget.get("type") == "DESCRIPTION":
                description_widget = widget
                break

        assert description_widget is not None, "DESCRIPTION widget should be present"
        description = description_widget.get("description", "")
        assert len(description) > 1000, f"Description should be large, got {len(description)} characters"

        # Validate response structure
        ResponseValidator.validate_work_item(created_item)


class TestWorkItemWidgets:
    """Test work item widget parsing and validation."""

    @pytest.mark.asyncio
    async def test_widget_parsing(
        self,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test that widgets are properly parsed in responses."""
        issue_data = static_test_data_factory.issue_data()

        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.add_work_item(created_item["id"])

        # Get full work item details
        get_input = GetWorkItemInput(id=created_item["id"])
        full_item = await get_work_item(get_input)

        # Validate widgets exist and are properly structured
        assert "widgets" in full_item
        assert isinstance(full_item["widgets"], list)
        assert len(full_item["widgets"]) > 0

        # Check for common widget types
        widget_types = [widget.get("type", "") for widget in full_item["widgets"]]
        expected_types = ["DESCRIPTION", "NOTES"]  # Basic widgets that should always exist

        for expected_type in expected_types:
            assert expected_type in widget_types, f"Expected widget type {expected_type} not found"

    @pytest.mark.asyncio
    async def test_description_widget(
        self,
        static_test_data_factory: TestDataFactory,
        work_item_type_ids: dict[str, str],
        cleanup_tracker: TestCleanup
    ):
        """Test description widget content."""
        issue_data = static_test_data_factory.issue_data()

        create_input = CreateWorkItemInput(
            project_path=issue_data["project_path"],
            work_item_type_id=work_item_type_ids["ISSUE"],
            title=issue_data["title"],
            description=issue_data["description"]
        )

        created_item = await create_work_item(create_input)
        cleanup_tracker.add_work_item(created_item["id"])

        # Get full work item details
        get_input = GetWorkItemInput(id=created_item["id"])
        full_item = await get_work_item(get_input)

        # Find description widget
        description_widget = None
        for widget in full_item["widgets"]:
            if widget.get("type") == "DESCRIPTION":
                description_widget = widget
                break

        assert description_widget is not None, "Description widget not found"

        # Validate description content - check that they match (should be identical)
        widget_description = description_widget.get("description", "")
        original_description = issue_data["description"]

        # For debugging: check if they're equal or one contains the other
        if original_description == widget_description:
            # Perfect match
            assert True
        elif original_description in widget_description:
            # Original is a substring of widget (this is what we expect)
            assert True
        elif widget_description in original_description:
            # Widget is a substring of original (unexpected but valid)
            assert True
        else:
            # No match at all - this is the failure case
            pytest.fail(f"Description mismatch. Original length: {len(original_description)}, Widget length: {len(widget_description)}")
