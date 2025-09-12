"""Tests for iteration management functions.

This module tests iteration-related functions:
- list_iterations

NOTE: Iterations are available in GitLab Premium/Ultimate and are group-level only.
Iterations are managed through iteration cadences and cannot be created directly via API.
GitLab REST API only supports listing iterations, not retrieving individual iterations.
Tests use existing iterations from the 'test' group which has pre-configured cadences.
"""

import pytest

from src.schemas.iterations import (
    ListIterationsInput,
)
from src.services.iterations import (
    list_iterations,
)


class TestIterationBasicOperations:
    """Test basic iteration operations using existing iterations."""

    @pytest.mark.asyncio
    async def test_list_iterations(self):
        """Test listing iterations in the test group with existing cadence iterations."""
        # Use the 'test' group which has existing iterations from cadence
        group_with_iterations = "test"

        # List iterations
        list_input = ListIterationsInput(
            group_id=group_with_iterations,
            per_page=20
        )

        iterations_response = await list_iterations(list_input)

        # Validate response structure
        assert "iterations" in iterations_response
        assert "count" in iterations_response
        assert isinstance(iterations_response["iterations"], list)
        assert iterations_response["count"] > 0, "Test group should have existing iterations from cadence"

        # Validate each iteration
        for iteration in iterations_response["iterations"]:
            assert "id" in iteration
            assert "state" in iteration
            assert "start_date" in iteration
            assert "due_date" in iteration
            # title can be None for auto-scheduled iterations
            assert iteration.get("title") is None or isinstance(iteration.get("title"), str)

        print(f"Successfully listed {iterations_response['count']} iterations")

    @pytest.mark.asyncio
    async def test_iteration_structure_validation(self):
        """Test that listed iterations have expected structure and fields."""
        # Use the 'test' group which has existing iterations from cadence
        group_with_iterations = "test"

        # List iterations to validate their structure
        list_input = ListIterationsInput(group_id=group_with_iterations, per_page=5)
        list_result = await list_iterations(list_input)

        # Ensure we have iterations to test with
        assert list_result["count"] > 0, "Test group should have existing iterations from cadence"

        # Validate structure of individual iterations
        first_iteration = list_result["iterations"][0]

        # Required fields that should be present
        required_fields = ["id", "iid", "sequence", "group_id", "state", "start_date", "due_date", "web_url"]
        for field in required_fields:
            assert field in first_iteration, f"Required field '{field}' missing from iteration"

        # Optional fields that may be None
        optional_fields = ["title", "description"]
        for field in optional_fields:
            if field in first_iteration:
                value = first_iteration[field]
                assert value is None or isinstance(value, str), f"Field '{field}' should be string or None"

        print(f"Successfully validated iteration structure for iteration {first_iteration['id']}: {first_iteration.get('title', '(auto-scheduled)')}")


class TestIterationFiltering:
    """Test iteration filtering and search capabilities."""

    @pytest.mark.asyncio
    async def test_list_iterations_with_state_filter(self):
        """Test listing iterations with state filtering."""
        group_with_iterations = "test"

        # Test different state filters
        states_to_test = ["opened", "closed", "all"]

        for state in states_to_test:
            list_input = ListIterationsInput(
                group_id=group_with_iterations,
                state=state,
                per_page=10
            )

            iterations_response = await list_iterations(list_input)

            # Validate response structure
            assert "iterations" in iterations_response
            assert isinstance(iterations_response["iterations"], list)
            print(f"State '{state}': found {iterations_response['count']} iterations")

    @pytest.mark.asyncio
    async def test_list_iterations_pagination(self):
        """Test iteration listing with pagination."""
        group_with_iterations = "test"

        # Test pagination
        list_input = ListIterationsInput(
            group_id=group_with_iterations,
            page=1,
            per_page=3
        )

        iterations_response = await list_iterations(list_input)

        # Should have limited results based on per_page
        assert "iterations" in iterations_response
        assert len(iterations_response["iterations"]) <= 3
        print(f"Pagination test: returned {len(iterations_response['iterations'])} iterations")


class TestIterationErrorHandling:
    """Test iteration error handling scenarios."""

    @pytest.mark.asyncio
    async def test_list_iterations_nonexistent_group(self):
        """Test listing iterations in non-existent group."""
        list_input = ListIterationsInput(
            group_id="nonexistent-group-12345"
        )

        with pytest.raises(Exception) as exc_info:
            await list_iterations(list_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])
