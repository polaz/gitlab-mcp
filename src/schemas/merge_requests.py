from .base import BaseModel, BaseResponseList


class CreateMergeRequestInput(BaseModel):
    """Input model for creating a merge request in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        source_branch: The source branch for the merge request.
        target_branch: The target branch for the merge request.
        title: The title of the merge request.
        description: The description of the merge request.
    """

    project_path: str
    source_branch: str
    target_branch: str
    title: str
    description: str | None = None


class GitLabMergeRequest(BaseModel):
    """Response model for a GitLab merge request.

    Attributes:
        id: The unique identifier of the merge request.
        iid: The internal ID of the merge request within the project.
        title: The title of the merge request.
        description: The description of the merge request.
        web_url: The web URL of the merge request.
    """

    id: int
    iid: int
    title: str
    description: str | None = None
    web_url: str


class ListMergeRequestsInput(BaseModel):
    """Input model for listing merge requests in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        state: The state of the merge requests to list (opened, closed, merged, or all).
        labels: The labels to filter merge requests by.
        order_by: The field to order merge requests by.
        sort: The direction to sort merge requests (asc or desc).
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    state: str | None = None
    labels: list[str] | None = None
    order_by: str | None = None
    sort: str | None = None
    page: int = 1
    per_page: int = 20


class GitLabMergeRequestListResponse(BaseResponseList[GitLabMergeRequest]):
    """Response model for listing GitLab merge requests."""

    pass


class GetMergeRequestInput(BaseModel):
    """Input model for getting a specific merge request from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
    """

    project_path: str
    mr_iid: int


class CreateMergeRequestCommentInput(BaseModel):
    """Input model for creating a comment on a GitLab merge request.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        body: The content of the comment.
    """

    project_path: str
    mr_iid: int
    body: str


class GitLabComment(BaseModel):
    """Response model for a GitLab comment.

    Attributes:
        id: The unique identifier of the comment.
        body: The content of the comment.
        author: Information about the author of the comment.
        created_at: The creation timestamp of the comment.
        updated_at: The last update timestamp of the comment.
    """

    id: int
    body: str
    author: dict[str, str | int]
    created_at: str
    updated_at: str | None = None


class GitLabCommentListResponse(BaseResponseList[GitLabComment]):
    """Response model for listing GitLab comments."""

    count: int


class ListMergeRequestCommentsInput(BaseModel):
    """Input model for listing comments on a GitLab merge request.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    mr_iid: int
    page: int = 1
    per_page: int = 20


class GetMergeRequestDiffInput(BaseModel):
    """Input model for getting the diff of a specific file in a GitLab merge request.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        file_path: The path of the file to get the diff for.
    """

    project_path: str
    mr_iid: int
    file_path: str


class GitLabMergeRequestChangesResponse(BaseModel):
    """Response model for the changes in a GitLab merge request.

    Attributes:
        mr_iid: The internal ID of the merge request within the project.
        files: Information about the files changed in the merge request.
        total_count: The total number of files changed.
    """

    mr_iid: int
    files: list[dict[str, str | bool | int]]
    total_count: int


class GitLabMergeRequestDiffResponse(BaseModel):
    """Response model for the diff of a specific file in a GitLab merge request.

    Attributes:
        mr_iid: The internal ID of the merge request within the project.
        file_path: The path of the file.
        diff: The diff of the file.
        old_path: The old path of the file.
        new_path: The new path of the file.
        renamed_file: Whether the file was renamed.
        deleted_file: Whether the file was deleted.
        new_file: Whether the file is new.
        content: The content of the file.
    """

    mr_iid: int
    file_path: str
    diff: str
    old_path: str
    new_path: str
    renamed_file: bool = False
    deleted_file: bool = False
    new_file: bool = False
    content: str | None = None


class SuggestMergeRequestCodeInput(BaseModel):
    """Input model for suggesting code changes in a GitLab merge request.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        file_path: The path of the file to suggest changes for.
        line_number: The line number to suggest changes for.
        suggested_code: The suggested code changes.
        comment: The comment explaining the suggestion.
        base_sha: The base commit SHA.
        start_sha: The start commit SHA.
        head_sha: The head commit SHA.
    """

    project_path: str
    mr_iid: int
    file_path: str
    line_number: int
    suggested_code: str
    comment: str
    base_sha: str | None = None
    start_sha: str | None = None
    head_sha: str | None = None


class ApproveMergeRequestInput(BaseModel):
    """Input model for approving a merge request."""

    project_path: str
    mr_iid: int
    sha: str | None = None


class MergeMergeRequestInput(BaseModel):
    """Input model for merging a merge request."""

    project_path: str
    mr_iid: int
    merge_commit_message: str | None = None
    should_remove_source_branch: bool = False
    merge_when_pipeline_succeeds: bool = False
    sha: str | None = None


class CloseMergeRequestInput(BaseModel):
    """Input model for closing a merge request."""

    project_path: str
    mr_iid: int
