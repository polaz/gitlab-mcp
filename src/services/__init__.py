# Re-export all service functions for easier imports

# Repository services
# Branch services
from .branches import (
    create_branch,
    create_branch_async,
    get_default_branch_ref,
    get_default_branch_ref_async,
)

# File services
from .files import (
    get_file_contents,
    get_file_contents_async,
)

# Group services (new)
from .groups import (
    create_group,
    create_group_async,
    delete_group,
    delete_group_async,
    get_group,
    get_group_async,
    list_groups,
    list_groups_async,
    update_group,
    update_group_async,
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
