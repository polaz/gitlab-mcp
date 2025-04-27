# Re-export all tool functions for easier imports

# Search tools
# Repository tools
# Branch tools
from .branches import (
    create_branch_tool,
    delete_branch_tool,
    delete_merged_branches_tool,
    get_branch_tool,
    get_default_branch_ref_tool,
    list_branches_tool,
    protect_branch_tool,
    unprotect_branch_tool,
)

# File tools
from .files import (
    create_file_tool,
)

# Group tools (new - read-only)
from .groups import (
    get_group_by_project_namespace_tool,
    get_group_tool,
    list_groups_tool,
)

# Issue tools
from .issues import (
    close_issue_tool,
    comment_on_issue_tool,
    create_issue_link_tool,
    create_issue_tool,
    delete_issue_link_tool,
    delete_issue_tool,
    get_issue_link_tool,
    get_issue_tool,
    list_all_issues_tool,
    list_group_issues_tool,
    list_issue_comments_tool,
    list_issue_links_tool,
    list_issues_tool,
    move_issue_tool,
    update_issue_tool,
)

# Job tools
from .jobs import (
    get_job_failure_info_tool,
    get_job_logs_tool,
    get_job_tool,
    list_pipeline_jobs_tool,
    list_pipeline_trigger_jobs_tool,
    list_project_jobs_tool,
)

# Merge request tools
from .merge_requests import (
    create_merge_request_tool,
    get_merge_request_tool,
    list_merge_requests_tool,
    merge_merge_request_tool,
)

# Pipeline tools (new)
from .pipelines import (
    get_latest_pipeline_tool,
    get_single_pipeline_tool,
    list_project_pipelines_tool,
)

# Repository tools
from .repositories import (
    create_repository_tool,
    list_repository_tree_tool,
)
from .search import (
    search_global_tool,
    search_group_tool,
    search_project_tool,
)

__all__ = [
    # Merge request tools
    # Issue tools
    "close_issue_tool",
    # Issue tools
    "comment_on_issue_tool",
    # Branch tools
    "create_branch_tool",
    # File tools
    "create_file_tool",
    "create_issue_link_tool",
    "create_issue_tool",
    "create_merge_request_tool",
    # Repository tools
    "create_repository_tool",
    "get_latest_pipeline_tool",
    "get_single_pipeline_tool",
    # Pipeline tools
    "list_project_pipelines_tool",
    "list_repository_tree_tool",
]
