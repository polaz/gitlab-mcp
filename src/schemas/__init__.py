# Re-export all schemas for easier imports

# Base schemas
from .base import GitLabResponseBase, PaginatedResponse, VisibilityLevel

# Branch schemas
from .branches import (
    CreateBranchInput,
    GetDefaultBranchRefInput,
    GitLabReference,
)

# File schemas
from .files import (
    GetFileContentsInput,
    GitLabContent,
)

# Group schemas (new)
from .groups import (
    CreateGroupInput,
    DeleteGroupInput,
    GetGroupInput,
    GitLabGroup,
    GitLabGroupListResponse,
    GroupAccessLevel,
    ListGroupsInput,
    UpdateGroupInput,
)

# Issue schemas
from .issues import (
    CreateIssueCommentInput,
    CreateIssueInput,
    GetIssueInput,
    GitLabIssue,
    GitLabIssueListResponse,
    ListIssueCommentsInput,
    ListIssuesInput,
)

# Merge request schemas
from .merge_requests import (
    CreateMergeRequestCommentInput,
    CreateMergeRequestInput,
    GetMergeRequestDiffInput,
    GetMergeRequestInput,
    GitLabComment,
    GitLabCommentListResponse,
    GitLabMergeRequest,
    GitLabMergeRequestChangesResponse,
    GitLabMergeRequestDiffResponse,
    GitLabMergeRequestListResponse,
    ListMergeRequestCommentsInput,
    ListMergeRequestsInput,
    SuggestMergeRequestCodeInput,
)

# Pipeline schemas (new)
from .pipelines import (
    CreatePipelineInput,
    GetPipelineInput,
    GitLabPipeline,
    GitLabPipelineListResponse,
    ListPipelinesInput,
    PipelineAction,
    PipelineActionInput,
    PipelineStatus,
)

# Repository schemas
from .repositories import (
    CreateRepositoryInput,
    ForkRepositoryInput,
    GitLabFork,
    GitLabRepository,
    GitLabSearchResponse,
    SearchProjectsInput,
)

# User schemas (new)
from .users import (
    BlockUserInput,
    CreateUserInput,
    GetUserInput,
    GitLabUser,
    GitLabUserListResponse,
    ListUsersInput,
    UnblockUserInput,
    UpdateUserInput,
    UserState,
)
