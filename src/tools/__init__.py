# Re-export all tool functions for easier imports

# Repository tools
# Branch tools
from .branches import (
    create_branch_tool,
    get_default_branch_ref_tool,
)

# File tools
from .files import (
    get_file_contents_tool,
)

# Group tools (new - read-only)
from .groups import (
    get_group_tool,
    list_groups_tool,
)

# Issue tools
from .issues import (
    close_issue_tool,
    comment_on_issue_tool,
    create_issue_tool,
    get_issue_tool,
    list_issue_comments_tool,
    list_issues_tool,
)

# Job tools
from .jobs import (
    get_job_logs_tool,
    get_job_tool,
    list_pipeline_jobs_tool,
)

# Merge request tools
from .merge_requests import (
    approve_merge_request_tool,
    close_merge_request_tool,
    comment_on_merge_request_tool,
    create_merge_request_tool,
    get_merge_request_diff_tool,
    get_merge_request_tool,
    list_merge_request_changes_tool,
    list_merge_request_comments_tool,
    list_merge_requests_tool,
    merge_merge_request_tool,
    suggest_code_in_merge_request_tool,
)

# Pipeline tools (new)
from .pipelines import (
    create_pipeline_tool,
    get_pipeline_tool,
    list_pipelines_tool,
    pipeline_action_tool,
)

# Repository tools
from .repositories import (
    create_repository_tool,
    fork_repository_tool,
    search_projects_tool,
)

# User tools (new - read-only)
from .users import (
    get_user_tool,
    list_users_tool,
)

__all__ = [
    "approve_merge_request_tool",
    "close_issue_tool",
    "close_merge_request_tool",
    "comment_on_issue_tool",
    "comment_on_merge_request_tool",
    "create_branch_tool",
    "create_issue_tool",
    "create_merge_request_tool",
    "create_pipeline_tool",
    "create_repository_tool",
    "fork_repository_tool",
    "get_default_branch_ref_tool",
    "get_file_contents_tool",
    "get_group_tool",
    "get_issue_tool",
    "get_merge_request_diff_tool",
    "get_merge_request_tool",
    "get_pipeline_tool",
    "get_user_tool",
    "list_groups_tool",
    "list_issue_comments_tool",
    "list_issues_tool",
    "list_merge_request_changes_tool",
    "list_merge_request_comments_tool",
    "list_merge_requests_tool",
    "list_pipelines_tool",
    "list_users_tool",
    "merge_merge_request_tool",
    "pipeline_action_tool",
    "search_projects_tool",
    "suggest_code_in_merge_request_tool",
]
