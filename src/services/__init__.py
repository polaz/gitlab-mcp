# Re-export all service functions for easier imports

# Repository services
# Branch services
from .branches import (
    create_branch,
    delete_branch,
    delete_merged_branches,
    get_branch,
    get_default_branch_ref,
    list_branches,
    protect_branch,
    unprotect_branch,
)

# File services
from .files import (
    create_file,
    delete_file,
    get_file_blame,
    get_file_contents,
    get_raw_file_contents,
    update_file,
)

# Group services (new)
from .groups import (
    get_group,
    get_group_by_project_namespace,
    list_groups,
)

# Issue services
from .issues import (
    comment_on_issue,
    comment_on_issue_async,
    create_issue,
    create_issue_async,
    get_issue,
    get_issue_async,
    list_issue_comments,
    list_issue_comments_async,
    list_issues,
    list_issues_async,
)

# Merge request services
from .merge_requests import (
    comment_on_merge_request,
    comment_on_merge_request_async,
    create_merge_request,
    create_merge_request_async,
    get_merge_request,
    get_merge_request_async,
    get_merge_request_diff,
    get_merge_request_diff_async,
    list_merge_request_changes,
    list_merge_request_changes_async,
    list_merge_request_comments,
    list_merge_request_comments_async,
    list_merge_requests,
    list_merge_requests_async,
    suggest_code_in_merge_request,
    suggest_code_in_merge_request_async,
)

# Pipeline services (new)
from .pipelines import (
    create_pipeline,
    create_pipeline_async,
    get_pipeline,
    get_pipeline_async,
    list_pipelines,
    list_pipelines_async,
    pipeline_action,
    pipeline_action_async,
)
from .repositories import (
    create_repository,
    create_repository_async,
    fork_project,
    fork_project_async,
    search_projects,
    search_projects_async,
)

# User services (new)
from .users import (
    block_user,
    block_user_async,
    create_user,
    create_user_async,
    get_user,
    get_user_async,
    list_users,
    list_users_async,
    unblock_user,
    unblock_user_async,
    update_user,
    update_user_async,
)
