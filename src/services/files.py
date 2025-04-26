"""Service functions for interacting with GitLab repository files using the REST API."""

import base64

from src.api.exceptions import (
    FileBlameError,
    FileContentError,
    FileCreateError,
    FileDeleteError,
    FileUpdateError,
    GitLabAPIError,
)
from src.api.rest_client import gitlab_rest_client
from src.schemas.files import (
    CreateFileInput,
    DeleteFileInput,
    FileBlameRange,
    FileOperationResponse,
    GetFileBlameInput,
    GetFileContentsInput,
    GetRawFileContentsInput,
    GitLabContent,
    UpdateFileInput,
)


async def get_file_contents(input_model: GetFileContentsInput) -> GitLabContent:
    """Retrieve the contents of a file from a GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path, file path, and ref.

    Returns:
        GitLabContent: The file contents.

    Raises:
        FileContentError: If retrieving the file content fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        ref = input_model.ref or "main"
        file_path = gitlab_rest_client._encode_path_parameter(input_model.file_path)

        endpoint = f"/projects/{project_path}/repository/files/{file_path}"
        params = {"ref": ref}

        data = await gitlab_rest_client.get_async(endpoint, params=params)

        # GitLab API returns base64 encoded content
        content = base64.b64decode(data["content"]).decode("utf-8")

        return GitLabContent(
            file_path=data["file_path"],
            content=content,
            encoding=data.get("encoding", "base64"),
            ref=ref,
            blob_id=data.get("blob_id"),
            commit_id=data.get("commit_id"),
            last_commit_id=data.get("last_commit_id"),
            content_sha256=data.get("content_sha256"),
            size=data.get("size"),
            execute_filemode=data.get("execute_filemode", False),
        )
    except Exception as exc:
        raise FileContentError(cause=exc) from exc


async def get_raw_file_contents(input_model: GetRawFileContentsInput) -> bytes:
    """Retrieve the raw contents of a file from a GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path, file path, and ref.

    Returns:
        bytes: The raw file contents.

    Raises:
        FileContentError: If retrieving the raw file content fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        ref = input_model.ref or "main"
        file_path = gitlab_rest_client._encode_path_parameter(input_model.file_path)

        endpoint = f"/projects/{project_path}/repository/files/{file_path}/raw"
        params = {"ref": ref}

        # This requires custom handling since we need the raw response
        client = gitlab_rest_client.get_httpx_client()
        headers = gitlab_rest_client._get_headers()

        response = await client.get(endpoint, headers=headers, params=params)
        if not response.is_success:
            gitlab_rest_client._handle_error_response(response)
    except Exception as exc:
        raise FileContentError(cause=exc) from exc
    else:
        return response.content


async def create_file(input_model: CreateFileInput) -> FileOperationResponse:
    """Create a new file in a GitLab repository using the REST API.

    Args:
        input_model: The input model containing file details and commit information.

    Returns:
        FileOperationResponse: Details of the created file.

    Raises:
        FileCreateError: If the file creation fails or the file already exists.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        file_path = gitlab_rest_client._encode_path_parameter(input_model.file_path)

        endpoint = f"/projects/{project_path}/repository/files/{file_path}"

        # Prepare payload
        payload = {
            "branch": input_model.branch,
            "content": input_model.content,
            "commit_message": input_model.commit_message,
            "encoding": input_model.encoding,
        }

        await gitlab_rest_client.post_async(endpoint, json_data=payload)

        return FileOperationResponse(
            file_path=input_model.file_path,
            branch=input_model.branch,
        )
    except GitLabAPIError as exc:
        if "already exists" in str(exc).lower():
            raise FileCreateError(cause=exc) from exc
        raise FileCreateError(cause=exc) from exc
    except Exception as exc:
        raise FileCreateError(cause=exc) from exc


async def update_file(input_model: UpdateFileInput) -> FileOperationResponse:
    """Update an existing file in a GitLab repository using the REST API.

    Args:
        input_model: The input model containing file details and commit information.

    Returns:
        FileOperationResponse: Details of the updated file.

    Raises:
        FileUpdateError: If the file update fails or the file doesn't exist.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        file_path = gitlab_rest_client._encode_path_parameter(input_model.file_path)

        endpoint = f"/projects/{project_path}/repository/files/{file_path}"

        # Prepare payload
        payload = {
            "branch": input_model.branch,
            "content": input_model.content,
            "commit_message": input_model.commit_message,
            "encoding": input_model.encoding,
        }

        if input_model.last_commit_id:
            payload["last_commit_id"] = input_model.last_commit_id

        await gitlab_rest_client.put_async(endpoint, json_data=payload)

        return FileOperationResponse(
            file_path=input_model.file_path,
            branch=input_model.branch,
        )
    except GitLabAPIError as exc:
        if "not exist" in str(exc).lower():
            raise FileUpdateError(cause=exc) from exc
        raise FileUpdateError(cause=exc) from exc
    except Exception as exc:
        raise FileUpdateError(cause=exc) from exc


async def delete_file(input_model: DeleteFileInput) -> None:
    """Delete a file from a GitLab repository using the REST API.

    Args:
        input_model: The input model containing file path, branch, and commit information.

    Raises:
        FileDeleteError: If the file deletion fails or the file doesn't exist.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        file_path = gitlab_rest_client._encode_path_parameter(input_model.file_path)

        endpoint = f"/projects/{project_path}/repository/files/{file_path}"

        # Prepare params
        params = {
            "branch": input_model.branch,
            "commit_message": input_model.commit_message,
        }

        await gitlab_rest_client.delete_async(endpoint, params=params)
    except GitLabAPIError as exc:
        if "not exist" in str(exc).lower():
            raise FileDeleteError(cause=exc) from exc
        raise FileDeleteError(cause=exc) from exc
    except Exception as exc:
        raise FileDeleteError(cause=exc) from exc


async def get_file_blame(input_model: GetFileBlameInput) -> list[FileBlameRange]:
    """Retrieve blame information for a file in a GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path, file path, and ref.

    Returns:
        list[FileBlameRange]: List of blame ranges with associated commits and lines.

    Raises:
        FileBlameError: If retrieving blame information fails or the file doesn't exist.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        file_path = gitlab_rest_client._encode_path_parameter(input_model.file_path)

        endpoint = f"/projects/{project_path}/repository/files/{file_path}/blame"

        # Prepare params
        params = {"ref": input_model.ref}

        # Add range parameters if provided
        if input_model.range_start is not None and input_model.range_end is not None:
            params["range[start]"] = str(input_model.range_start)
            params["range[end]"] = str(input_model.range_end)

        blame_data = await gitlab_rest_client.get_async(endpoint, params=params)
    except GitLabAPIError as exc:
        if "not exist" in str(exc).lower():
            raise FileBlameError(cause=exc) from exc
        raise FileBlameError(cause=exc) from exc
    except Exception as exc:
        raise FileBlameError(cause=exc) from exc
    else:
        # Convert to our schema
        blame_ranges = []
        for range_data in blame_data:
            blame_range = FileBlameRange(
                commit=range_data["commit"],
                lines=range_data["lines"],
            )
            blame_ranges.append(blame_range)
        return blame_ranges
