"""Tests for milestone management functions.

This module tests all milestone-related functions:
- create_milestone
- get_milestone
- list_milestones
- update_milestone
- delete_milestone
"""


import time

import pytest

from src.schemas.milestones import (
    CreateMilestoneInput,
    DeleteMilestoneInput,
    GetMilestoneInput,
    ListMilestonesInput,
    UpdateMilestoneInput,
)
from src.services.milestones import (
    create_milestone,
    delete_milestone,
    get_milestone,
    list_milestones,
    update_milestone,
)
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory
from tests.utils.validators import BulkValidator, ResponseValidator


class TestMilestoneBasicOperations:
    """Test basic milestone CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_milestone(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a new milestone."""
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description=milestone_data["description"],
            due_date=milestone_data["due_date"],
            start_date=milestone_data["start_date"]
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Validate creation
        ResponseValidator.validate_milestone(created_milestone)
        assert created_milestone["title"] == milestone_data["title"]
        assert created_milestone["description"] == milestone_data["description"]
        assert created_milestone["state"] == "active"

    @pytest.mark.asyncio
    async def test_get_milestone(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test getting a specific milestone."""
        # Create a milestone first
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description=milestone_data["description"]
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Get the milestone
        get_input = GetMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"]
        )

        retrieved_milestone = await get_milestone(get_input)

        # Validate retrieval
        ResponseValidator.validate_milestone(retrieved_milestone)
        assert retrieved_milestone["id"] == created_milestone["id"]
        assert retrieved_milestone["title"] == milestone_data["title"]

    @pytest.mark.asyncio
    async def test_list_milestones(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test listing milestones in a project."""
        # Create a few milestones
        milestone_titles = []
        for i in range(2):
            milestone_data = static_test_data_factory.milestone_data()
            milestone_data["title"] = f"TEST List Milestone {i+1}"
            milestone_titles.append(milestone_data["title"])

            create_input = CreateMilestoneInput(
                project_path=static_test_project_path,
                title=milestone_data["title"],
                description=f"Test milestone {i+1} for listing"
            )

            created_milestone = await create_milestone(create_input)
            cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # List milestones
        list_input = ListMilestonesInput(
            project_path=static_test_project_path,
            state="active",
            per_page=20
        )

        milestones_response = await list_milestones(list_input)

        # Handle structured response (Pydantic model with 'milestones' field)
        if isinstance(milestones_response, dict) and 'milestones' in milestones_response:
            milestones = milestones_response['milestones']
        else:
            milestones = milestones_response

        # Validate listing
        assert isinstance(milestones, list)
        assert len(milestones) >= 2  # At least our test milestones

        # Validate each milestone
        for milestone in milestones:
            ResponseValidator.validate_milestone(milestone)

        # Check our test milestones are in the list
        found_titles = [m["title"] for m in milestones]
        for title in milestone_titles:
            assert title in found_titles

    @pytest.mark.asyncio
    async def test_update_milestone(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test updating a milestone."""
        # Create a milestone first
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description="Original description"
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Update the milestone
        new_title = f"Updated {milestone_data['title']}"
        new_description = "Updated description with new information"

        update_input = UpdateMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"],
            title=new_title,
            description=new_description
        )

        updated_milestone = await update_milestone(update_input)

        # Validate update
        ResponseValidator.validate_milestone(updated_milestone)
        assert updated_milestone["id"] == created_milestone["id"]
        assert updated_milestone["title"] == new_title
        assert updated_milestone["description"] == new_description

    @pytest.mark.asyncio
    async def test_delete_milestone(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory
    ):
        """Test deleting a milestone."""
        # Create a milestone first
        milestone_data = static_test_data_factory.milestone_data()
        milestone_data["title"] = f"DELETE_TEST {milestone_data['title']}"

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description="Milestone for deletion test"
        )

        created_milestone = await create_milestone(create_input)

        # Delete the milestone
        delete_input = DeleteMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"]
        )

        result = await delete_milestone(delete_input)

        # Validate deletion
        assert "message" in result or "success" in str(result).lower()

        # Verify milestone is gone
        get_input = GetMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"]
        )

        with pytest.raises((ValueError, KeyError, RuntimeError, Exception)):  # Should raise an error for deleted milestone
            await get_milestone(get_input)


class TestMilestoneStates:
    """Test milestone state management."""

    @pytest.mark.asyncio
    async def test_milestone_state_transitions(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test milestone state transitions (active <-> closed)."""
        # Create active milestone
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description="Milestone for state testing"
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        assert created_milestone["state"] == "active"

        # Close the milestone
        update_input = UpdateMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"],
            state_event="close"
        )

        closed_milestone = await update_milestone(update_input)

        # Validate state change
        assert closed_milestone["state"] == "closed"
        assert closed_milestone["id"] == created_milestone["id"]

        # Reopen the milestone
        update_input = UpdateMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"],
            state_event="activate"
        )

        reopened_milestone = await update_milestone(update_input)

        # Validate state change
        assert reopened_milestone["state"] == "active"

    @pytest.mark.asyncio
    async def test_list_milestones_by_state(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test listing milestones filtered by state."""
        # Create active milestone
        active_data = static_test_data_factory.milestone_data()
        active_data["title"] = f"ACTIVE {active_data['title']}"

        create_active = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=active_data["title"],
            description="Active milestone"
        )

        active_milestone = await create_milestone(create_active)
        cleanup_tracker.add_milestone(active_milestone["id"], static_test_project_path)

        # Create and close another milestone
        closed_data = static_test_data_factory.milestone_data()
        closed_data["title"] = f"CLOSED {closed_data['title']}"

        create_closed = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=closed_data["title"],
            description="Milestone to be closed"
        )

        closed_milestone = await create_milestone(create_closed)
        cleanup_tracker.add_milestone(closed_milestone["id"], static_test_project_path)

        # Close the second milestone
        update_input = UpdateMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=closed_milestone["id"],
            state_event="close"
        )

        await update_milestone(update_input)

        # List active milestones
        list_active = ListMilestonesInput(
            project_path=static_test_project_path,
            state="active"
        )

        active_response = await list_milestones(list_active)
        active_milestones = active_response['milestones'] if isinstance(active_response, dict) and 'milestones' in active_response else active_response
        active_titles = [m["title"] for m in active_milestones]

        # List closed milestones
        list_closed = ListMilestonesInput(
            project_path=static_test_project_path,
            state="closed"
        )

        closed_response = await list_milestones(list_closed)
        closed_milestones = closed_response['milestones'] if isinstance(closed_response, dict) and 'milestones' in closed_response else closed_response
        closed_titles = [m["title"] for m in closed_milestones]

        # Validate filtering
        assert active_data["title"] in active_titles
        assert closed_data["title"] in closed_titles
        assert active_data["title"] not in closed_titles
        assert closed_data["title"] not in active_titles


class TestMilestoneDates:
    """Test milestone date handling."""

    @pytest.mark.asyncio
    async def test_milestone_with_dates(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating milestone with start and due dates."""
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description="Milestone with dates",
            start_date=milestone_data["start_date"],
            due_date=milestone_data["due_date"]
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Validate dates
        ResponseValidator.validate_milestone(created_milestone)
        assert "start_date" in created_milestone
        assert "due_date" in created_milestone

        # Dates should be preserved
        if created_milestone["start_date"]:
            assert milestone_data["start_date"] in created_milestone["start_date"]
        if created_milestone["due_date"]:
            assert milestone_data["due_date"] in created_milestone["due_date"]

    @pytest.mark.asyncio
    async def test_update_milestone_dates(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test updating milestone dates."""
        # Create milestone without dates
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description="Milestone for date update"
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Update with dates
        new_dates = static_test_data_factory.milestone_data()

        update_input = UpdateMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=created_milestone["id"],
            start_date=new_dates["start_date"],
            due_date=new_dates["due_date"]
        )

        updated_milestone = await update_milestone(update_input)

        # Validate date update
        ResponseValidator.validate_milestone(updated_milestone)
        assert "start_date" in updated_milestone
        assert "due_date" in updated_milestone


class TestMilestoneErrorHandling:
    """Test milestone error handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_milestone(
        self,
        static_test_project_path: str
    ):
        """Test getting a milestone that doesn't exist."""
        get_input = GetMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=999999
        )

        with pytest.raises(Exception) as exc_info:
            await get_milestone(get_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_create_milestone_duplicate_title(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating milestone with duplicate title."""
        milestone_data = static_test_data_factory.milestone_data()

        # Create first milestone
        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description="First milestone"
        )

        first_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(first_milestone["id"], static_test_project_path)

        # Try to create milestone with same title
        duplicate_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],  # Same title
            description="Duplicate milestone"
        )

        with pytest.raises(Exception) as exc_info:
            await create_milestone(duplicate_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["exists", "taken", "duplicate", "conflict", "already being used", "validation failed"])

    @pytest.mark.asyncio
    async def test_update_nonexistent_milestone(
        self,
        static_test_project_path: str
    ):
        """Test updating a milestone that doesn't exist."""
        update_input = UpdateMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=999999,
            title="This should fail"
        )

        with pytest.raises(Exception) as exc_info:
            await update_milestone(update_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_delete_nonexistent_milestone(
        self,
        static_test_project_path: str
    ):
        """Test deleting a milestone that doesn't exist."""
        delete_input = DeleteMilestoneInput(
            project_path=static_test_project_path,
            milestone_id=999999
        )

        with pytest.raises(Exception) as exc_info:
            await delete_milestone(delete_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])


class TestMilestoneEdgeCases:
    """Test milestone edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_milestone_unicode_content(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating milestone with Unicode content."""
        unicode_data = static_test_data_factory.unicode_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=unicode_data["title"],
            description=unicode_data["description"]
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Validate Unicode handling
        ResponseValidator.validate_milestone(created_milestone)
        assert created_milestone["title"] == unicode_data["title"]
        assert created_milestone["description"] == unicode_data["description"]

    @pytest.mark.asyncio
    async def test_milestone_minimal_fields(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating milestone with only required fields."""
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"]
            # No description, dates, etc.
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Validate minimal creation
        ResponseValidator.validate_milestone(created_milestone)
        assert created_milestone["title"] == milestone_data["title"]
        assert created_milestone["state"] == "active"

    @pytest.mark.asyncio
    async def test_milestone_long_description(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating milestone with very long description."""
        large_data = static_test_data_factory.large_content_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=large_data["name"],  # Use 'name' field from large_content_data
            description=large_data["description"][:2000]  # Limit for milestone
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Validate large content handling
        ResponseValidator.validate_milestone(created_milestone)
        assert len(created_milestone["description"]) > 500


class TestMilestonePerformance:
    """Test milestone performance scenarios."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_list_milestones_performance(
        self,
        static_test_project_path: str
    ):
        """Test milestone listing performance."""

        list_input = ListMilestonesInput(
            project_path=static_test_project_path,
            per_page=50
        )

        start_time = time.time()
        milestones_response = await list_milestones(list_input)
        end_time = time.time()

        # Performance validation (should complete within 5 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 5.0)

        # Handle structured response
        milestones = milestones_response['milestones'] if isinstance(milestones_response, dict) and 'milestones' in milestones_response else milestones_response

        # Validate response structure
        assert isinstance(milestones, list)
        for milestone in milestones[:5]:  # Validate first 5 milestones
            ResponseValidator.validate_milestone(milestone)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_bulk_milestone_operations(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating and managing multiple milestones."""

        # Create multiple milestones
        batch_size = 3  # Small number for testing
        created_milestones = []

        start_time = time.time()

        for i in range(batch_size):
            milestone_data = static_test_data_factory.milestone_data()
            milestone_data["title"] = f"BULK_TEST {i}_{milestone_data['title']}"

            create_input = CreateMilestoneInput(
                project_path=static_test_project_path,
                title=milestone_data["title"],
                description=f"Bulk test milestone {i+1}"
            )

            created_milestone = await create_milestone(create_input)
            created_milestones.append(created_milestone)
            cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

            # Validate each milestone
            ResponseValidator.validate_milestone(created_milestone)

        end_time = time.time()

        # Validate bulk creation
        BulkValidator.validate_bulk_creation(created_milestones, batch_size)
        BulkValidator.validate_performance_metrics(start_time, end_time, 30.0)

        # Verify all milestones were created with unique IDs
        milestone_ids = [milestone["id"] for milestone in created_milestones]
        assert len(set(milestone_ids)) == batch_size


class TestMilestoneFieldValidation:
    """Test milestone field validation and edge cases."""

    @pytest.mark.asyncio
    async def test_milestone_field_order(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test that milestone responses have proper field ordering for UX."""
        # Create a milestone
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"],
            description=milestone_data["description"]
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Validate field ordering for UX (important fields first)
        # Note: GitLab API returns fields in specific order, adjust expectations
        expected_important_fields = ["id", "title", "description"]  # Use actually early fields
        ResponseValidator.validate_field_order(created_milestone, expected_important_fields)

    @pytest.mark.asyncio
    async def test_milestone_minimal_response(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test that milestone responses contain all required fields."""
        # Create a milestone
        milestone_data = static_test_data_factory.milestone_data()

        create_input = CreateMilestoneInput(
            project_path=static_test_project_path,
            title=milestone_data["title"]
        )

        created_milestone = await create_milestone(create_input)
        cleanup_tracker.add_milestone(created_milestone["id"], static_test_project_path)

        # Check required fields are present
        required_fields = ["id", "title", "state", "web_url", "created_at", "updated_at"]
        for field in required_fields:
            assert field in created_milestone, f"Required field '{field}' missing from milestone response"
            assert created_milestone[field] is not None, f"Required field '{field}' is None"
