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
        blob_id: The blob ID of the file.
        commit_id: The commit ID that contains the file.
        last_commit_id: The ID of the last commit that modified the file.
        content_sha256: The SHA256 hash of the file content.
        size: The size of the file in bytes.
        execute_filemode: Whether the file has execute permissions.
    """

    file_path: str
    content: str
    encoding: str | None = None
    ref: str | None = None
    blob_id: str | None = None
    commit_id: str | None = None
    last_commit_id: str | None = None
    content_sha256: str | None = None
    size: int | None = None
    execute_filemode: bool = False


class CreateFileInput(BaseModel):
    """Input model for creating a file in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file within the repository.
        branch: The branch name to create the file in.
        content: The content of the file.
        commit_message: The commit message.
        encoding: The encoding of the file content (default: text).
    """

    project_path: str
    file_path: str
    branch: str
    content: str
    commit_message: str
    encoding: str = "text"


class UpdateFileInput(BaseModel):
    """Input model for updating a file in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file within the repository.
        branch: The branch name to update the file in.
        content: The new content of the file.
        commit_message: The commit message.
        encoding: The encoding of the file content (default: text).
        last_commit_id: The last commit ID that modified the file (optional).
    """

    project_path: str
    file_path: str
    branch: str
    content: str
    commit_message: str
    encoding: str = "text"
    last_commit_id: str | None = None


class DeleteFileInput(BaseModel):
    """Input model for deleting a file from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file within the repository.
        branch: The branch name to delete the file from.
        commit_message: The commit message.
    """

    project_path: str
    file_path: str
    branch: str
    commit_message: str


class GetRawFileContentsInput(BaseModel):
    """Input model for retrieving raw file contents from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file within the repository.
        ref: The reference (branch, tag, or commit) to get the file from.
    """

    project_path: str
    file_path: str
    ref: str | None = None


class GetFileBlameInput(BaseModel):
    """Input model for retrieving blame information for a file.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        file_path: The path of the file within the repository.
        ref: The reference (branch, tag, or commit) to get the blame from.
        range_start: The starting line number (optional).
        range_end: The ending line number (optional).
    """

    project_path: str
    file_path: str
    ref: str
    range_start: int | None = None
    range_end: int | None = None


class FileBlameCommit(BaseModel):
    """Model for a commit in a file blame response.

    Attributes:
        id: The commit ID.
        message: The commit message.
        parent_ids: The parent commit IDs.
        authored_date: The date the commit was authored.
        author_name: The name of the author.
        author_email: The email of the author.
        committed_date: The date the commit was committed.
        committer_name: The name of the committer.
        committer_email: The email of the committer.
    """

    id: str
    message: str
    parent_ids: list[str]
    authored_date: str
    author_name: str
    author_email: str
    committed_date: str
    committer_name: str
    committer_email: str


class FileBlameRange(BaseModel):
    """Model for a range in a file blame response.

    Attributes:
        commit: The commit information.
        lines: The lines in this range.
    """

    commit: FileBlameCommit
    lines: list[str]


class FileOperationResponse(GitLabResponseBase):
    """Response model for file operations.

    Attributes:
        file_path: The path of the file within the repository.
        branch: The branch name the operation was performed on.
    """

    file_path: str
    branch: str
