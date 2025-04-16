from pydantic import BaseModel

from .base import GitLabResponseBase


class GetFileContentsInput(BaseModel):
    """Input model for retrieving file contents from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file within the repository.
        ref: The reference (branch, tag, or commit) to get the file from.
    """

    project_path: str
    file_path: str
    ref: str | None = None


class GitLabContent(GitLabResponseBase):
    """Response model for file contents from a GitLab repository.

    Attributes:
        file_path: The path of the file within the repository.
        content: The content of the file.
        encoding: The encoding of the file content.
        ref: The reference (branch, tag, or commit) the file was retrieved from.
    """

    file_path: str
    content: str
    encoding: str | None = None
    ref: str | None = None
