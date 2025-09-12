"""Tests for file management functions.

This module tests all file-related functions:
- get_file_contents
- create_file
- update_file
- delete_file
- get_file_tree
- get_file_raw
"""



import time

import pytest

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.files import (
    CreateFileInput,
    DeleteFileInput,
    GetFileContentsInput,
    GetFileRawInput,
    GetFileTreeInput,
    UpdateFileInput,
)
from src.services.files import (
    create_file,
    delete_file,
    get_file_contents,
    get_file_raw,
    get_file_tree,
    update_file,
)
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory
from tests.utils.validators import BulkValidator


class TestFileBasicOperations:
    """Test basic file operations."""

    @pytest.mark.asyncio
    async def test_get_file_contents_readme(
        self,
        static_test_project_path: str,
        cleanup_tracker: TestCleanup
    ):
        """Test getting contents of a file - creates README if needed."""
        readme_path = "README.md"

        # First, try to get existing README
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=readme_path,
            ref="main"
        )

        try:
            file_content = await get_file_contents(get_input)
        except Exception:
            # README doesn't exist, create it for the test
            create_input = CreateFileInput(
                project_path=static_test_project_path,
                file_path=readme_path,
                branch="main",
                content="# Test Repository\n\nThis is a test repository for GitLab MCP server testing.",
                commit_message="Add README.md for testing"
            )

            await create_file(create_input)
            cleanup_tracker.add_file(static_test_project_path, readme_path, "main")

            # Now get the file content
            file_content = await get_file_contents(get_input)

        # Validate response structure - file_content is a Pydantic model
        assert hasattr(file_content, 'content')
        assert hasattr(file_content, 'file_path')
        assert file_content.content is not None
        assert file_content.file_path == readme_path

    @pytest.mark.asyncio
    async def test_get_file_tree_root(
        self,
        static_test_project_path: str
    ):
        """Test getting file tree from repository root."""
        tree_input = GetFileTreeInput(
            project_path=static_test_project_path,
            path="",
            ref="main"
        )

        file_tree = await get_file_tree(tree_input)

        # Validate response structure
        assert isinstance(file_tree, list)
        assert len(file_tree) > 0

        # Validate each tree item
        for item in file_tree:
            assert "name" in item
            assert "type" in item
            assert "path" in item
            assert item["type"] in ["blob", "tree"]  # File or directory

    @pytest.mark.asyncio
    async def test_get_file_raw(
        self,
        static_test_project_path: str
    ):
        """Test getting raw file contents."""
        # First get file tree to find a file
        tree_input = GetFileTreeInput(
            project_path=static_test_project_path,
            path="",
            ref="main"
        )

        file_tree = await get_file_tree(tree_input)

        # Find a blob (file) to test with
        test_file = None
        for item in file_tree:
            if item["type"] == "blob":
                test_file = item["path"]
                break

        if not test_file:
            # No files found, create a test file for this test
            test_file_path = "test_file_raw.txt"
            create_input = CreateFileInput(
                project_path=static_test_project_path,
                file_path=test_file_path,
                branch="main",
                content="Test content for raw file access",
                commit_message="Add test file for raw access testing"
            )

            await create_file(create_input)
            test_file = test_file_path

        # Get raw content
        raw_input = GetFileRawInput(
            project_path=static_test_project_path,
            file_path=test_file,
            ref="main"
        )

        raw_content = await get_file_raw(raw_input)

        # Validate raw content response
        assert isinstance(raw_content, str | bytes)


class TestFileCreation:
    """Test file creation functionality."""

    @pytest.mark.asyncio
    async def test_create_text_file(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a new text file."""
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/test-{file_data['name']}.txt"
        file_content = "This is a test file created by the test suite.\n\nContent for testing file operations."

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=file_content,
            commit_message=f"Create test file {file_path}",
            branch="main"
        )

        created_file = await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Validate creation
        assert hasattr(created_file, "file_path")
        assert created_file.file_path == file_path
        assert hasattr(created_file, "branch")
        assert created_file.branch == "main"

        # Verify file exists by reading it back
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path,
            ref="main"
        )

        retrieved_file = await get_file_contents(get_input)
        assert retrieved_file.content == file_content

    @pytest.mark.asyncio
    async def test_create_json_file(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a JSON file with structured content."""
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/test-{file_data['name']}.json"

        json_content = '''{{
    "name": "test-config",
    "version": "1.0.0",
    "description": "Test configuration file",
    "settings": {{
        "debug": true,
        "timeout": 30
    }}
}}'''

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=json_content,
            commit_message="Add test JSON configuration",
            branch="main"
        )

        created_file = await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Validate creation
        assert created_file.file_path == file_path

        # Verify content is preserved
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path
        )

        retrieved_file = await get_file_contents(get_input)
        assert retrieved_file.content == json_content

    @pytest.mark.asyncio
    async def test_create_file_in_subdirectory(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a file in a subdirectory."""
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/subdirectory/nested-{file_data['name']}.md"

        markdown_content = f"""# Test Document

This is a test markdown file created in a subdirectory.

## Features

- File creation in nested directories
- Markdown content preservation
- Automated testing

Created: {file_data['timestamp']}
"""

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=markdown_content,
            commit_message="Create nested test file",
            branch="main"
        )

        created_file = await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Validate creation
        assert created_file.file_path == file_path

        # Verify file exists in tree
        tree_input = GetFileTreeInput(
            project_path=static_test_project_path,
            path="test-files/subdirectory"
        )

        file_tree = await get_file_tree(tree_input)
        file_names = [item["name"] for item in file_tree]
        expected_name = f"nested-{file_data['name']}.md"
        assert expected_name in file_names


class TestFileUpdates:
    """Test file update functionality."""

    @pytest.mark.asyncio
    async def test_update_file_content(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test updating file content."""
        # Create a file first
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/update-{file_data['name']}.txt"
        original_content = "Original content for update testing."

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=original_content,
            commit_message="Create file for update test",
            branch="main"
        )

        await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Update the file
        updated_content = "Updated content with new information.\n\nThis file has been modified."

        update_input = UpdateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=updated_content,
            commit_message="Update test file content",
            branch="main"
        )

        updated_file = await update_file(update_input)

        # Validate update
        assert updated_file.file_path == file_path

        # Verify updated content
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path
        )

        retrieved_file = await get_file_contents(get_input)
        assert retrieved_file.content == updated_content
        assert retrieved_file.content != original_content

    @pytest.mark.asyncio
    async def test_update_file_multiple_times(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test updating a file multiple times."""
        # Create initial file
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/multi-update-{file_data['name']}.txt"

        versions = [
            "Version 1: Initial content",
            "Version 2: First update",
            "Version 3: Second update with more changes"
        ]

        # Create file with first version
        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=versions[0],
            commit_message="Create multi-update test file",
            branch="main"
        )

        await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Update file multiple times
        for i, content in enumerate(versions[1:], 1):
            update_input = UpdateFileInput(
                project_path=static_test_project_path,
                file_path=file_path,
                content=content,
                commit_message=f"Update {i}: test file",
                branch="main"
            )

            await update_file(update_input)

        # Verify final content
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path
        )

        final_file = await get_file_contents(get_input)
        assert final_file.content == versions[-1]


class TestFileDeletion:
    """Test file deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_file(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory
    ):
        """Test deleting a file."""
        # Create a file first
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/delete-{file_data['name']}.txt"

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content="This file will be deleted.",
            commit_message="Create file for deletion test",
            branch="main"
        )

        await create_file(create_input)

        # Verify file exists
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path
        )

        file_before_delete = await get_file_contents(get_input)
        assert file_before_delete.file_path == file_path

        # Delete the file
        delete_input = DeleteFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            commit_message="Delete test file",
            branch="main"
        )

        delete_result = await delete_file(delete_input)

        # Validate deletion
        assert delete_result is True

        # Verify file is gone
        with pytest.raises(GitLabAPIError):  # Should raise an error when file not found
            await get_file_contents(get_input)


class TestFileErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_file(
        self,
        static_test_project_path: str
    ):
        """Test getting a file that doesn't exist."""
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path="nonexistent-file-12345.txt"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await get_file_contents(get_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404"])

    @pytest.mark.asyncio
    async def test_create_file_duplicate(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating a file that already exists."""
        # Create a file first
        file_data = static_test_data_factory.file_data()
        file_path = f"test-files/duplicate-{file_data['name']}.txt"

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content="Original file content",
            commit_message="Create original file",
            branch="main"
        )

        await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Try to create the same file again
        duplicate_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content="Duplicate file content",
            commit_message="Try to create duplicate",
            branch="main"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await create_file(duplicate_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["exists", "conflict", "already"])

    @pytest.mark.asyncio
    async def test_update_nonexistent_file(
        self,
        static_test_project_path: str
    ):
        """Test updating a file that doesn't exist."""
        update_input = UpdateFileInput(
            project_path=static_test_project_path,
            file_path="nonexistent-update-file.txt",
            content="This update should fail",
            commit_message="Update nonexistent file",
            branch="main"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await update_file(update_input)

        # Validate error response
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ["not found", "does not exist", "404", "failed"])

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(
        self,
        static_test_project_path: str
    ):
        """Test deleting a file that doesn't exist."""
        delete_input = DeleteFileInput(
            project_path=static_test_project_path,
            file_path="nonexistent-delete-file.txt",
            commit_message="Delete nonexistent file",
            branch="main"
        )

        # Delete nonexistent file should return False, not raise an exception
        delete_result = await delete_file(delete_input)
        assert delete_result is False


class TestFileEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_file_unicode_content(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating files with Unicode content."""
        unicode_data = static_test_data_factory.unicode_data()
        file_path = f"test-files/unicode-{hash(unicode_data['title']) % 1000}.txt"

        unicode_content = f"""Unicode Test File: {unicode_data['title']}

Description: {unicode_data['description']}

Special characters: 中文, العربية, Русский, 日本語, 한국어
Emojis: 🚀 🎉 💻 🌟 🔥
Mathematical symbols: ∑ ∆ ∞ ∂ ∫
"""

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=unicode_content,
            commit_message="Create Unicode test file",
            branch="main"
        )

        await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Verify Unicode content preservation
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path
        )

        retrieved_file = await get_file_contents(get_input)
        assert retrieved_file.content == unicode_content

    @pytest.mark.asyncio
    async def test_file_large_content(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating files with large content."""
        large_data = static_test_data_factory.large_content_data()
        file_path = f"test-files/large-{large_data['name']}.txt"

        # Create content that's large but not excessive (for CI limitations)
        large_content = large_data["description"][:5000]  # Limit to 5KB

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=file_path,
            content=large_content,
            commit_message="Create large content test file",
            branch="main"
        )

        await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        # Verify large content preservation
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=file_path
        )

        retrieved_file = await get_file_contents(get_input)
        assert len(retrieved_file.content) > 1000
        assert retrieved_file.content == large_content

    @pytest.mark.asyncio
    async def test_file_special_characters_path(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating files with special characters in path."""
        file_data = static_test_data_factory.file_data()
        # Use safe special characters for file paths
        special_path = f"test-files/special_chars-{file_data['name']}.txt"

        create_input = CreateFileInput(
            project_path=static_test_project_path,
            file_path=special_path,
            content="File with special characters in path",
            commit_message="Create file with special path",
            branch="main"
        )

        created_file = await create_file(create_input)
        cleanup_tracker.add_file(static_test_project_path, special_path, "main")

        # Verify file creation with special path
        assert created_file.file_path == special_path

        # Verify file is accessible
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=special_path
        )

        retrieved_file = await get_file_contents(get_input)
        assert retrieved_file.file_path == special_path


class TestFilePerformance:
    """Test file performance scenarios."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_get_file_tree_performance(
        self,
        static_test_project_path: str
    ):
        """Test file tree retrieval performance."""

        tree_input = GetFileTreeInput(
            project_path=static_test_project_path,
            path=""
        )

        start_time = time.time()
        file_tree = await get_file_tree(tree_input)
        end_time = time.time()

        # Performance validation (should complete within 5 seconds)
        BulkValidator.validate_performance_metrics(start_time, end_time, 5.0)

        # Validate response structure
        assert isinstance(file_tree, list)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_bulk_file_operations(
        self,
        static_test_project_path: str,
        static_test_data_factory: TestDataFactory,
        cleanup_tracker: TestCleanup
    ):
        """Test creating and managing multiple files."""

        # Create multiple files
        batch_size = 3  # Small number for testing
        created_files = []

        start_time = time.time()

        for i in range(batch_size):
            file_data = static_test_data_factory.file_data()
            file_path = f"test-files/bulk-{i}-{file_data['name']}.txt"

            create_input = CreateFileInput(
                project_path=static_test_project_path,
                file_path=file_path,
                content=f"Bulk test file {i+1}\n\nContent for file {i+1}",
                commit_message=f"Create bulk test file {i+1}",
                branch="main"
            )

            created_file = await create_file(create_input)
            created_files.append(created_file)
            cleanup_tracker.add_file(static_test_project_path, file_path, "main")

        end_time = time.time()

        # Validate bulk creation
        BulkValidator.validate_bulk_creation(created_files, batch_size, "file")
        BulkValidator.validate_performance_metrics(start_time, end_time, 30.0)

        # Verify all files were created with unique paths
        file_paths = [file.file_path for file in created_files]
        assert len(set(file_paths)) == batch_size


class TestFileFieldValidation:
    """Test file field validation and edge cases."""

    @pytest.mark.asyncio
    async def test_file_response_structure(
        self,
        static_test_project_path: str
    ):
        """Test that file responses have consistent structure."""
        # Get file tree to find a file
        tree_input = GetFileTreeInput(
            project_path=static_test_project_path,
            path=""
        )

        file_tree = await get_file_tree(tree_input)

        # Find a file to test with
        test_file_path = None
        for item in file_tree:
            if item["type"] == "blob":
                test_file_path = item["path"]
                break

        if not test_file_path:
            # No files found, create a test file for this test
            test_file_path = "test_file_structure.txt"
            create_input = CreateFileInput(
                project_path=static_test_project_path,
                file_path=test_file_path,
                branch="main",
                content="Test content for file structure validation",
                commit_message="Add test file for structure validation testing"
            )

            await create_file(create_input)

        # Get file contents
        get_input = GetFileContentsInput(
            project_path=static_test_project_path,
            file_path=test_file_path
        )

        file_content = await get_file_contents(get_input)

        # Check required fields are present
        required_fields = ["content", "file_path"]  # file_name is not a field in GitLabContent
        for field in required_fields:
            assert hasattr(file_content, field), f"Required field '{field}' missing from file response"

    @pytest.mark.asyncio
    async def test_file_tree_structure(
        self,
        static_test_project_path: str
    ):
        """Test that file tree responses have consistent structure."""
        tree_input = GetFileTreeInput(
            project_path=static_test_project_path,
            path=""
        )

        file_tree = await get_file_tree(tree_input)

        # Validate each tree item
        for item in file_tree:
            required_fields = ["name", "type", "path"]
            for field in required_fields:
                assert field in item, f"Required field '{field}' missing from tree item"
                assert item[field] is not None, f"Field '{field}' is None"

            # Validate type values
            assert item["type"] in ["blob", "tree"], f"Invalid type: {item['type']}"
