from typing import Any

from pydantic import BaseModel

from .base import GitLabResponseBase


class CreateBranchInput(BaseModel):
    """Input model for creating a new branch in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        branch_name: The name of the branch to create.
        ref: The reference (branch, tag, or commit) to create the branch from.
    """

    project_path: str
    branch_name: str
    ref: str


class GitLabReference(GitLabResponseBase):
    """Response model for a GitLab branch or reference.

    Attributes:
        name: The name of the branch or reference.
        commit: Details about the commit the reference points to.
    """

    name: str
    commit: dict[str, Any]


class GetDefaultBranchRefInput(BaseModel):
    """Input model for getting the default branch of a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
    """

    project_path: str
