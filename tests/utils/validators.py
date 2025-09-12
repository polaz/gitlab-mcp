"""Response validators for GitLab MCP Server tests.

This module provides utilities for validating API responses
and ensuring data integrity across all GitLab functions.
"""

from datetime import datetime
from typing import Any
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, field: str, expected: Any, actual: Any, message: str | None = None):
        self.field = field
        self.expected = expected
        self.actual = actual
        self.message = message or f"Validation failed for {field}: expected {expected}, got {actual}"
        super().__init__(self.message)


class ResponseValidator:
    """Validates GitLab API responses against expected schemas and patterns."""

    @staticmethod
    def validate_id_field(data: dict[str, Any] | Any, field_name: str = "id") -> bool:
        """Validate that an ID field exists and has a valid value."""
        # Handle both dict and Pydantic model
        if isinstance(data, dict):
            if field_name not in data:
                raise ValidationError(field_name, "present", "missing", f"Missing required field: {field_name}")
            value = data[field_name]
        else:
            # Pydantic model or object with attributes
            if not hasattr(data, field_name):
                raise ValidationError(field_name, "present", "missing", f"Missing required field: {field_name}")
            value = getattr(data, field_name)

        if isinstance(value, str):
            # GraphQL global ID format
            if value.startswith("gid://gitlab/"):
                return True
            # Regular string ID
            if value.strip():
                return True
        elif isinstance(value, int):
            # Numeric ID
            if value > 0:
                return True

        raise ValidationError(field_name, "valid ID", value, f"Invalid ID format: {value}")

    @staticmethod
    def validate_title_field(data: dict[str, Any] | Any, field_name: str = "title") -> bool:
        """Validate that a title field exists and is non-empty."""
        # Handle both dict and Pydantic model
        if isinstance(data, dict):
            if field_name not in data:
                raise ValidationError(field_name, "present", "missing")
            value = data[field_name]
        else:
            # Pydantic model or object with attributes
            if not hasattr(data, field_name):
                raise ValidationError(field_name, "present", "missing")
            value = getattr(data, field_name)

        if not isinstance(value, str) or not value.strip():
            raise ValidationError(field_name, "non-empty string", value)

        return True

    @staticmethod
    def validate_url_field(data: dict[str, Any], field_name: str = "web_url") -> bool:
        """Validate that a URL field exists and is a valid URL."""
        if field_name not in data:
            raise ValidationError(field_name, "present", "missing")

        value = data[field_name]
        if not isinstance(value, str):
            raise ValidationError(field_name, "string URL", type(value).__name__)

        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                raise ValidationError(field_name, "valid URL", value)
        except Exception:
            raise ValidationError(field_name, "valid URL", value) from None

        return True

    @staticmethod
    def validate_date_field(data: dict[str, Any], field_name: str, required: bool = True) -> bool:
        """Validate that a date field has a valid ISO format."""
        if field_name not in data:
            if required:
                raise ValidationError(field_name, "present", "missing")
            return True

        value = data[field_name]
        if value is None and not required:
            return True

        if isinstance(value, datetime):
            # Already a datetime object, that's valid
            return True
        elif isinstance(value, str):
            try:
                # Try to parse as ISO format
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError as e:
                raise ValidationError(field_name, "ISO date format", value) from e
        else:
            raise ValidationError(field_name, "ISO date string or datetime object", type(value).__name__)

        return True

    @staticmethod
    def validate_state_field(data: dict[str, Any], valid_states: list[str], field_name: str = "state") -> bool:
        """Validate that a state field has one of the expected values."""
        if field_name not in data:
            raise ValidationError(field_name, "present", "missing")

        value = data[field_name]
        if value not in valid_states:
            raise ValidationError(field_name, f"one of {valid_states}", value)

        return True

    @staticmethod
    def validate_array_field(data: dict[str, Any], field_name: str, min_length: int = 0) -> bool:
        """Validate that an array field exists and meets length requirements."""
        if field_name not in data:
            raise ValidationError(field_name, "present", "missing")

        value = data[field_name]
        if not isinstance(value, list):
            raise ValidationError(field_name, "array", type(value).__name__)

        if len(value) < min_length:
            raise ValidationError(field_name, f"at least {min_length} items", f"{len(value)} items")

        return True

    @staticmethod
    def validate_work_item(work_item: dict[str, Any]) -> bool:
        """Validate a work item response structure."""
        # Required fields
        ResponseValidator.validate_id_field(work_item, "id")
        ResponseValidator.validate_id_field(work_item, "iid")
        ResponseValidator.validate_title_field(work_item, "title")
        ResponseValidator.validate_state_field(work_item, ["OPEN", "CLOSED"], "state")
        ResponseValidator.validate_url_field(work_item, "webUrl")
        ResponseValidator.validate_date_field(work_item, "createdAt")
        ResponseValidator.validate_date_field(work_item, "updatedAt")

        # Work item type
        if "workItemType" not in work_item:
            raise ValidationError("workItemType", "present", "missing")

        work_item_type = work_item["workItemType"]
        ResponseValidator.validate_id_field(work_item_type, "id")
        ResponseValidator.validate_title_field(work_item_type, "name")

        # Author
        if "author" not in work_item:
            raise ValidationError("author", "present", "missing")

        author = work_item["author"]
        ResponseValidator.validate_id_field(author, "id")
        ResponseValidator.validate_title_field(author, "name")

        # Widgets (should be array, but only present in detailed queries)
        if "widgets" in work_item:
            ResponseValidator.validate_array_field(work_item, "widgets")

        return True

    @staticmethod
    def validate_milestone(milestone: dict[str, Any]) -> bool:
        """Validate a milestone response structure."""
        ResponseValidator.validate_id_field(milestone, "id")
        ResponseValidator.validate_title_field(milestone, "title")
        ResponseValidator.validate_state_field(milestone, ["active", "closed"], "state")
        ResponseValidator.validate_url_field(milestone, "web_url")
        ResponseValidator.validate_date_field(milestone, "created_at")
        ResponseValidator.validate_date_field(milestone, "updated_at")
        ResponseValidator.validate_date_field(milestone, "due_date", required=False)
        ResponseValidator.validate_date_field(milestone, "start_date", required=False)

        return True

    @staticmethod
    def validate_repository(repository: dict[str, Any]) -> bool:
        """Validate a repository response structure."""
        ResponseValidator.validate_id_field(repository, "id")
        ResponseValidator.validate_title_field(repository, "name")
        ResponseValidator.validate_url_field(repository, "web_url")
        ResponseValidator.validate_date_field(repository, "created_at")
        ResponseValidator.validate_date_field(repository, "last_activity_at", required=False)

        # Path fields
        for field in ["path", "path_with_namespace"]:
            if field in repository:
                value = repository[field]
                if not isinstance(value, str) or not value.strip():
                    raise ValidationError(field, "non-empty string", value)

        # Visibility
        if "visibility" in repository:
            valid_visibility = ["private", "internal", "public"]
            ResponseValidator.validate_state_field(repository, valid_visibility, "visibility")

        return True

    @staticmethod
    def validate_branch(branch: dict[str, Any]) -> bool:
        """Validate a branch response structure."""
        ResponseValidator.validate_title_field(branch, "name")

        # Commit info
        if "commit" in branch:
            commit = branch["commit"]
            ResponseValidator.validate_id_field(commit, "id")
            ResponseValidator.validate_date_field(commit, "committed_date", required=False)

        # Protection status
        if "protected" in branch and not isinstance(branch["protected"], bool):
            raise ValidationError("protected", "boolean", type(branch["protected"]).__name__)

        return True

    @staticmethod
    def validate_merge_request(merge_request: dict[str, Any]) -> bool:
        """Validate a merge request response structure."""
        ResponseValidator.validate_id_field(merge_request, "id")
        ResponseValidator.validate_id_field(merge_request, "iid")
        ResponseValidator.validate_title_field(merge_request, "title")
        ResponseValidator.validate_url_field(merge_request, "web_url")
        ResponseValidator.validate_date_field(merge_request, "created_at")
        ResponseValidator.validate_date_field(merge_request, "updated_at")

        # State validation
        valid_states = ["opened", "closed", "merged"]
        ResponseValidator.validate_state_field(merge_request, valid_states, "state")

        # Source and target branches
        for field in ["source_branch", "target_branch"]:
            if field in merge_request:
                value = merge_request[field]
                if not isinstance(value, str) or not value.strip():
                    raise ValidationError(field, "non-empty string", value)

        return True

    @staticmethod
    def validate_group(group: dict[str, Any]) -> bool:
        """Validate a group response structure."""
        ResponseValidator.validate_id_field(group, "id")
        ResponseValidator.validate_title_field(group, "name")
        ResponseValidator.validate_url_field(group, "web_url")

        # Path fields
        for field in ["path", "full_path"]:
            if field in group:
                value = group[field]
                if not isinstance(value, str) or not value.strip():
                    raise ValidationError(field, "non-empty string", value)

        # Visibility
        if "visibility" in group:
            valid_visibility = ["private", "internal", "public"]
            ResponseValidator.validate_state_field(group, valid_visibility, "visibility")

        return True

    @staticmethod
    def validate_search_result(result: dict[str, Any], expected_type: str) -> bool:
        """Validate a search result based on its expected type."""
        validators = {
            "projects": ResponseValidator.validate_repository,
            "issues": lambda x: ResponseValidator.validate_id_field(x, "id") and ResponseValidator.validate_title_field(x, "title"),
            "merge_requests": lambda x: ResponseValidator.validate_id_field(x, "id") and ResponseValidator.validate_title_field(x, "title"),
            "blobs": lambda x: "filename" in x and "data" in x,
            "wiki_blobs": lambda x: "filename" in x and "data" in x,
        }

        validator = validators.get(expected_type)
        if validator:
            return validator(result)

        # Generic validation
        ResponseValidator.validate_id_field(result, "id")
        return True

    @staticmethod
    def validate_pagination_info(data: dict[str, Any]) -> bool:
        """Validate pagination information in responses."""
        pagination_fields = ["page", "per_page", "total", "total_pages"]

        for field in pagination_fields:
            if field in data:
                value = data[field]
                if not isinstance(value, int) or value < 0:
                    raise ValidationError(field, "non-negative integer", value)

        return True

    @staticmethod
    def validate_error_response(data: dict[str, Any]) -> bool:
        """Validate error response structure."""
        if "message" not in data and "error" not in data:
            raise ValidationError("error_info", "message or error field", "missing")

        return True

    @staticmethod
    def validate_list_response(data: list[dict[str, Any]], validator_func, min_count: int = 0) -> bool:
        """Validate a list response with individual item validation."""
        if not isinstance(data, list):
            raise ValidationError("response_type", "list", type(data).__name__)

        if len(data) < min_count:
            raise ValidationError("item_count", f"at least {min_count}", len(data))

        for i, item in enumerate(data):
            try:
                validator_func(item)
            except ValidationError as e:
                raise ValidationError(f"item[{i}].{e.field}", e.expected, e.actual,
                                    f"Item {i} validation failed: {e.message}") from e

        return True

    @staticmethod
    def validate_field_order(data: dict[str, Any], expected_first_fields: list[str]) -> bool:
        """Validate that important fields appear first (for UX)."""
        if not isinstance(data, dict):
            return True

        data_keys = list(data.keys())

        for i, expected_field in enumerate(expected_first_fields):
            if expected_field in data_keys:
                actual_index = data_keys.index(expected_field)
                if actual_index > i:
                    raise ValidationError(
                        f"field_order.{expected_field}",
                        f"position {i} or earlier",
                        f"position {actual_index}",
                        f"Field {expected_field} should appear earlier for better UX"
                    )

        return True

    @staticmethod
    def validate_test_data_cleanup(data: dict[str, Any], test_prefix: str) -> bool:
        """Validate that test data has proper prefixes for identification."""
        title_fields = ["title", "name", "subject"]

        for field in title_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str) and test_prefix in value:
                    return True

        # If no title field found or doesn't contain prefix, it might be non-test data
        raise ValidationError(
            "test_data_identification",
            f"title containing '{test_prefix}'",
            "no identifiable test data marker",
            "This may not be test data and could be real user data"
        )


class BulkValidator:
    """Validates bulk operations and large datasets."""

    @staticmethod
    def validate_bulk_creation(results: list, expected_count: int, item_type: str = "generic") -> bool:
        """Validate bulk creation results with schema-specific validation.

        Args:
            results: List of created items (can be Pydantic models or dicts)
            expected_count: Expected number of items
            item_type: Type of items being validated for schema-specific validation
                      Options: "branch", "work_item", "milestone", "file", "generic"
        """
        if len(results) != expected_count:
            raise ValidationError("bulk_count", expected_count, len(results))

        # Validate each item based on its specific schema
        for i, item in enumerate(results):
            try:
                BulkValidator._validate_single_item(item, item_type, i)
            except ValidationError as e:
                # Re-raise with bulk context
                raise ValidationError(f"bulk_item[{i}]", e.expected, e.actual, e.message) from None

        return True

    @staticmethod
    def _validate_branch_item(item_dict: dict) -> None:
        """Validate a branch item."""
        ResponseValidator.validate_title_field(item_dict, "name")
        if "commit" in item_dict:
            ResponseValidator.validate_id_field(item_dict["commit"], "id")

    @staticmethod
    def _validate_work_item_item(item_dict: dict) -> None:
        """Validate a work item."""
        ResponseValidator.validate_id_field(item_dict, "id")
        if "iid" in item_dict:
            ResponseValidator.validate_id_field(item_dict, "iid")

    @staticmethod
    def _validate_milestone_item(item_dict: dict) -> None:
        """Validate a milestone item."""
        ResponseValidator.validate_id_field(item_dict, "id")
        ResponseValidator.validate_id_field(item_dict, "iid")

    @staticmethod
    def _validate_file_item(item_dict: dict) -> None:
        """Validate a file item."""
        if "file_path" not in item_dict and "path" not in item_dict:
            raise ValidationError("file_identifier", "file_path or path", "missing")

    @staticmethod
    def _validate_generic_item(item_dict: dict) -> None:
        """Validate a generic item with common identifier patterns."""
        has_identifier = False
        for id_field in ["id", "iid", "name", "path"]:
            if id_field in item_dict:
                if id_field in ["id", "iid"]:
                    ResponseValidator.validate_id_field(item_dict, id_field)
                else:
                    ResponseValidator.validate_title_field(item_dict, id_field)
                has_identifier = True
                break

        if not has_identifier:
            raise ValidationError("identifier", "id, iid, name, or path", "missing")

    @staticmethod
    def _validate_single_item(item, item_type: str, index: int) -> None:
        """Validate a single item based on its type."""
        # Convert Pydantic model to dict for validation if needed
        item_dict = item.model_dump() if hasattr(item, 'model_dump') else item

        # Schema-specific validation
        validators = {
            "branch": BulkValidator._validate_branch_item,
            "work_item": BulkValidator._validate_work_item_item,
            "milestone": BulkValidator._validate_milestone_item,
            "file": BulkValidator._validate_file_item,
        }

        validator = validators.get(item_type)
        if validator:
            validator(item_dict)
        else:
            BulkValidator._validate_generic_item(item_dict)

    @staticmethod
    def validate_performance_metrics(start_time: float, end_time: float, max_duration: float) -> bool:
        """Validate that operations complete within acceptable time."""
        duration = end_time - start_time

        if duration > max_duration:
            raise ValidationError(
                "performance",
                f"<= {max_duration}s",
                f"{duration:.2f}s",
                f"Operation took too long: {duration:.2f}s > {max_duration}s"
            )

        return True
