from mcp.server.fastmcp import FastMCP

from src.tools import (
    approve_merge_request_tool,
    close_issue_tool,
    close_merge_request_tool,
    comment_on_issue_tool,
    comment_on_merge_request_tool,
    # Branch tools
    create_branch_tool,
    # Issue tools
    create_issue_tool,
    # Merge request tools
    create_merge_request_tool,
    create_pipeline_tool,
    create_repository_tool,
    # Repository tools
    fork_repository_tool,
    get_default_branch_ref_tool,
    # File tools
    get_file_contents_tool,
    get_group_tool,
    get_issue_tool,
    # Job tools
    get_job_logs_tool,
    get_job_tool,
    get_merge_request_diff_tool,
    get_merge_request_tool,
    get_pipeline_tool,
    get_user_tool,
    # Group tools (new - read-only)
    list_groups_tool,
    list_issue_comments_tool,
    list_issues_tool,
    list_merge_request_changes_tool,
    list_merge_request_comments_tool,
    list_merge_requests_tool,
    # Pipeline tools (new)
    list_pipeline_jobs_tool,
    list_pipelines_tool,
    # User tools (new - read-only)
    list_users_tool,
    merge_merge_request_tool,
    pipeline_action_tool,
    search_projects_tool,
    suggest_code_in_merge_request_tool,
)

# Create the MCP server
mcp = FastMCP("Gitlab")

# Register repository tools
mcp.tool(name="fork_repository", description="Fork a GitLab repository.")(
    fork_repository_tool
)
mcp.tool(name="create_repository", description="Create a new GitLab repository.")(
    create_repository_tool
)
mcp.tool(
    name="search_projects", description="Search for GitLab projects by name or keyword."
)(search_projects_tool)

# Register branch tools
mcp.tool(
    name="create_branch", description="Create a new branch in a GitLab repository."
)(create_branch_tool)
mcp.tool(
    name="get_default_branch_ref",
    description="Get the default branch reference for a GitLab repository.",
)(get_default_branch_ref_tool)

# Register file tools
mcp.tool(
    name="get_file_contents",
    description="Retrieve the contents of a file from a GitLab repository.",
)(get_file_contents_tool)


# Register issue tools
mcp.tool(name="create_issue", description="Create a new issue in a GitLab repository.")(
    create_issue_tool
)
mcp.tool(name="list_issues", description="List issues for a GitLab project.")(
    list_issues_tool
)
mcp.tool(name="get_issue", description="Get details for a specific GitLab issue.")(
    get_issue_tool
)
mcp.tool(name="comment_on_issue", description="Add a comment to a GitLab issue.")(
    comment_on_issue_tool
)
mcp.tool(name="list_issue_comments", description="List comments for a GitLab issue.")(
    list_issue_comments_tool
)
mcp.tool(name="close_issue", description="Close a GitLab issue.")(close_issue_tool)

# Register merge request tools
mcp.tool(
    name="create_merge_request",
    description="Create a new merge request in a GitLab repository.",
)(create_merge_request_tool)
mcp.tool(
    name="list_merge_requests", description="List merge requests for a GitLab project."
)(list_merge_requests_tool)
mcp.tool(
    name="get_merge_request",
    description="Get details for a specific GitLab merge request.",
)(get_merge_request_tool)
mcp.tool(
    name="comment_on_merge_request",
    description="Add a comment to a GitLab merge request.",
)(comment_on_merge_request_tool)
mcp.tool(
    name="list_merge_request_comments",
    description="List comments for a GitLab merge request.",
)(list_merge_request_comments_tool)
mcp.tool(
    name="list_merge_request_changes",
    description="List files changed in a GitLab merge request.",
)(list_merge_request_changes_tool)
mcp.tool(
    name="get_merge_request_diff",
    description="Get the diff for a specific file in a GitLab merge request.",
)(get_merge_request_diff_tool)
mcp.tool(
    name="suggest_code_in_merge_request",
    description="Create a code suggestion comment on a GitLab merge request.",
)(suggest_code_in_merge_request_tool)
mcp.tool(name="approve_merge_request", description="Approve a GitLab merge request.")(
    approve_merge_request_tool
)
mcp.tool(name="merge_merge_request", description="Merge a GitLab merge request.")(
    merge_merge_request_tool
)
mcp.tool(name="close_merge_request", description="Close a GitLab merge request.")(
    close_merge_request_tool
)

# Register pipeline tools (new)
mcp.tool(name="list_pipelines", description="List pipelines in a GitLab project.")(
    list_pipelines_tool
)
mcp.tool(
    name="get_pipeline", description="Get a specific pipeline from a GitLab project."
)(get_pipeline_tool)
mcp.tool(
    name="create_pipeline", description="Create a new pipeline in a GitLab project."
)(create_pipeline_tool)
mcp.tool(
    name="pipeline_action",
    description="Perform an action on a GitLab pipeline (cancel or retry).",
)(pipeline_action_tool)

# Register job tools
mcp.tool(
    name="list_pipeline_jobs",
    description="List jobs in a GitLab pipeline.",
)(list_pipeline_jobs_tool)
mcp.tool(
    name="get_job",
    description="Get a specific job from a GitLab project.",
)(get_job_tool)
mcp.tool(
    name="get_job_logs",
    description="Get logs from a GitLab job.",
)(get_job_logs_tool)

# Register group tools (new - read-only)
mcp.tool(name="list_groups", description="List GitLab groups.")(list_groups_tool)
mcp.tool(name="get_group", description="Get a specific GitLab group.")(get_group_tool)

# Register user tools (new - read-only)
mcp.tool(name="list_users", description="List GitLab users.")(list_users_tool)
mcp.tool(name="get_user", description="Get a specific GitLab user.")(get_user_tool)

# Run the server
if __name__ == "__main__":
    mcp.run()
