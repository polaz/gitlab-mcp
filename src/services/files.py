from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.files import (
    GetFileContentsInput,
    GitLabContent,
)


def get_file_contents(input_model: GetFileContentsInput) -> GitLabContent:
    """Retrieve the contents of a file from a GitLab repository.

    Args:
        input_model: The input model containing project path, file path, and ref.

    Returns:
        GitLabContent: The file contents.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(id=input_model.project_path)

        # Get the file
        f = project.files.get(
            file_path=input_model.file_path, ref=input_model.ref or "main"
        )

        # Map to our schema
        return GitLabContent(
            file_path=f.path,
            content=f.decode().decode("utf-8"),
            encoding=f.encoding,
            ref=input_model.ref,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


# Async versions of the functions
get_file_contents_async = to_async(get_file_contents)
