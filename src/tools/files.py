"""Tool functions for working with GitLab repository files."""

import asyncio
from dataclasses import dataclass
from typing import Any

from src.api.exceptions import (
    FileBlameError,
    FileContentError,
    FileCreateError,
    FileDeleteError,
    FileUpdateError,
    GitLabAPIError,
)
from src.schemas.files import (
    CreateFileInput,
    DeleteFileInput,
    GetFileBlameInput,
    GetFileContentsInput,
    GetRawFileContentsInput,
    UpdateFileInput,
)
from src.services.files import (
    create_file,
    delete_file,
    get_file_blame,
    get_file_contents,
    get_raw_file_contents,
    update_file,
)


@dataclass
class FileOptions:
    """Additional options for file operations."""

    encoding: str = "text"
    last_commit_id: str | None = None


def get_file_contents_tool(
    project_path: str, file_path: str, ref: str | None = None
) -> dict[str, Any]:
    """Retrieve the contents of a file from a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file to retrieve.
        ref: Optional reference (branch, tag, or commit) to get the file from.

    Returns:
        dict[str, Any]: The file contents.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetFileContentsInput(
            project_path=project_path,
            file_path=file_path,
            ref=ref,
        )

        # Call service function
        response = asyncio.run(get_file_contents(input_model))

        # Convert to dict
        return response.model_dump()
    except (GitLabAPIError, FileContentError) as exc:
        raise ValueError(str(exc)) from exc


def get_raw_file_contents_tool(
    project_path: str, file_path: str, ref: str | None = None
) -> bytes:
    """Retrieve the raw contents of a file from a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file to retrieve.
        ref: Optional reference (branch, tag, or commit) to get the file from.

    Returns:
        bytes: The raw file contents.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetRawFileContentsInput(
            project_path=project_path,
            file_path=file_path,
            ref=ref,
        )

        # Call service function
        return asyncio.run(get_raw_file_contents(input_model))
    except (GitLabAPIError, FileContentError) as exc:
        raise ValueError(str(exc)) from exc


def create_file_tool(
    project_path: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    options: FileOptions | None = None,
) -> dict[str, Any]:
    """Create a new file in a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file to create.
        branch: The branch name to create the file in.
        content: The content of the file.
        commit_message: The commit message.
        options: Optional file operation options.

    Returns:
        dict[str, Any]: Details of the created file.

    Raises:
        ValueError: If the GitLab API returns an error or the file already exists.
    """
    try:
        # Extract options if provided
        encoding = "text"
        if options:
            encoding = options.encoding

        # Create input model
        input_model = CreateFileInput(
            project_path=project_path,
            file_path=file_path,
            branch=branch,
            content=content,
            commit_message=commit_message,
            encoding=encoding,
        )

        # Call service function
        response = asyncio.run(create_file(input_model))

        # Convert to dict
        return response.model_dump()
    except (GitLabAPIError, FileCreateError) as exc:
        raise ValueError(str(exc)) from exc


def update_file_tool(
    project_path: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    options: FileOptions | None = None,
) -> dict[str, Any]:
    """Update an existing file in a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file to update.
        branch: The branch name to update the file in.
        content: The new content of the file.
        commit_message: The commit message.
        options: Optional file operation options.

    Returns:
        dict[str, Any]: Details of the updated file.

    Raises:
        ValueError: If the GitLab API returns an error or the file doesn't exist.
    """
    try:
        # Extract options if provided
        encoding = "text"
        last_commit_id = None
        if options:
            encoding = options.encoding
            last_commit_id = options.last_commit_id

        # Create input model
        input_model = UpdateFileInput(
            project_path=project_path,
            file_path=file_path,
            branch=branch,
            content=content,
            commit_message=commit_message,
            encoding=encoding,
            last_commit_id=last_commit_id,
        )

        # Call service function
        response = asyncio.run(update_file(input_model))

        # Convert to dict
        return response.model_dump()
    except (GitLabAPIError, FileUpdateError) as exc:
        raise ValueError(str(exc)) from exc


def delete_file_tool(
    project_path: str,
    file_path: str,
    branch: str,
    commit_message: str,
) -> None:
    """Delete a file from a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file to delete.
        branch: The branch name to delete the file from.
        commit_message: The commit message.

    Raises:
        ValueError: If the GitLab API returns an error or the file doesn't exist.
    """
    try:
        # Create input model
        input_model = DeleteFileInput(
            project_path=project_path,
            file_path=file_path,
            branch=branch,
            commit_message=commit_message,
        )

        # Call service function
        asyncio.run(delete_file(input_model))
    except (GitLabAPIError, FileDeleteError) as exc:
        raise ValueError(str(exc)) from exc


def get_file_blame_tool(
    project_path: str,
    file_path: str,
    ref: str,
    range_start: int | None = None,
    range_end: int | None = None,
) -> list[dict[str, Any]]:
    """Retrieve blame information for a file in a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file to get blame for.
        ref: The reference (branch, tag, or commit) to get the blame from.
        range_start: Optional starting line number.
        range_end: Optional ending line number.

    Returns:
        list[dict[str, Any]]: List of blame ranges with associated commits and lines.

    Raises:
        ValueError: If the GitLab API returns an error or the file doesn't exist.
    """
    try:
        # Create input model
        input_model = GetFileBlameInput(
            project_path=project_path,
            file_path=file_path,
            ref=ref,
            range_start=range_start,
            range_end=range_end,
        )

        # Call service function
        response = asyncio.run(get_file_blame(input_model))

        # Convert to list of dicts
        return [blame_range.model_dump() for blame_range in response]
    except (GitLabAPIError, FileBlameError) as exc:
        raise ValueError(str(exc)) from exc
