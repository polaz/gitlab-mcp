from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.files import (
    GetFileContentsInput,
)
from ..services.files import (
    get_file_contents,
)


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
        response = get_file_contents(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
