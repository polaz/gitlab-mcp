from mcp.server.fastmcp import FastMCP

from src.tools.branches import (
    create_branch_tool,
    delete_branch_tool,
    delete_merged_branches_tool,
    get_branch_tool,
    get_default_branch_ref_tool,
    list_branches_tool,
    protect_branch_tool,
    unprotect_branch_tool,
)
from src.tools.files import (
    create_file_tool,
    delete_file_tool,
    get_file_blame_tool,
    get_file_contents_tool,
    get_raw_file_contents_tool,
    update_file_tool,
)
from src.tools.groups import (
    get_group_by_project_namespace_tool,
    get_group_tool,
    list_groups_tool,
)
from src.tools.issues import (
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
from src.tools.jobs import (
    get_job_failure_info_tool,
    get_job_logs_tool,
    get_job_tool,
)
from src.tools.merge_requests import (
    create_merge_request_tool,
    get_merge_request_tool,
    list_merge_requests_tool,
    merge_merge_request_tool,
)
from src.tools.pipelines import (
    get_latest_pipeline_tool,
    get_single_pipeline_tool,
    list_project_pipelines_tool,
)
from src.tools.repositories import create_repository_tool
from src.tools.search import (
    search_global_tool,
    search_group_tool,
    search_project_tool,
)

# Create the MCP server
mcp = FastMCP("Gitlab", instructions="This server exposes GitLab operations as MCP tools. Use the tool names and descriptions to interact with GitLab resources.")

# Register repository tools

mcp.tool(name="create_repository", description="Create a new GitLab repository.")(
    create_repository_tool
)


# Register branch tools
mcp.tool(
    name="create_branch", description="Create a new branch in a GitLab repository."
)(create_branch_tool)
mcp.tool(
    name="get_default_branch_ref",
    description="Get the default branch reference for a GitLab repository.",
)(get_default_branch_ref_tool)
mcp.tool(
    name="list_branches",
    description="List branches in a GitLab repository.",
)(list_branches_tool)
mcp.tool(
    name="get_branch",
    description="Get details for a specific GitLab branch.",
)(get_branch_tool)
mcp.tool(
    name="delete_branch",
    description="Delete a branch from a GitLab repository.",
)(delete_branch_tool)
mcp.tool(
    name="delete_merged_branches",
    description="Delete all merged branches from a GitLab repository.",
)(delete_merged_branches_tool)
mcp.tool(
    name="protect_branch",
    description="Protect a branch in a GitLab repository.",
)(protect_branch_tool)
mcp.tool(
    name="unprotect_branch",
    description="Remove protection from a branch in a GitLab repository.",
)(unprotect_branch_tool)

# Register file tools

mcp.tool(
    name="create_file",
    description="Create a new file in a GitLab repository.",
)(create_file_tool)
mcp.tool(
    name="get_file_contents",
    description="Retrieve the contents of a file from a GitLab repository.",
)(get_file_contents_tool)
mcp.tool(
    name="get_raw_file_contents",
    description="Retrieve the raw contents of a file from a GitLab repository.",
)(get_raw_file_contents_tool)
mcp.tool(
    name="update_file",
    description="Update an existing file in a GitLab repository.",
)(update_file_tool)
mcp.tool(
    name="delete_file",
    description="Delete a file from a GitLab repository.",
)(delete_file_tool)
mcp.tool(
    name="get_file_blame",
    description="Retrieve blame information for a file in a GitLab repository.",
)(get_file_blame_tool)

# Register issue tools
mcp.tool(name="create_issue", description="Create a new issue in a GitLab repository.")(
    create_issue_tool
)
mcp.tool(
    name="update_issue", description="Update an existing issue in a GitLab repository."
)(update_issue_tool)
mcp.tool(name="list_issues", description="List issues for a GitLab project.")(
    list_issues_tool
)
mcp.tool(
    name="list_all_issues",
    description="List all issues the authenticated user has access to.",
)(list_all_issues_tool)
mcp.tool(name="list_group_issues", description="List issues in a GitLab group.")(
    list_group_issues_tool
)
mcp.tool(name="get_issue", description="Get details for a specific GitLab issue.")(
    get_issue_tool
)
mcp.tool(name="close_issue", description="Close a GitLab issue.")(close_issue_tool)
mcp.tool(name="delete_issue", description="Delete an issue from a GitLab repository.")(
    delete_issue_tool
)
mcp.tool(name="move_issue", description="Move an issue to a different project.")(
    move_issue_tool
)
mcp.tool(name="comment_on_issue", description="Add a comment to a GitLab issue.")(
    comment_on_issue_tool
)
mcp.tool(name="list_issue_comments", description="List comments for a GitLab issue.")(
    list_issue_comments_tool
)
mcp.tool(name="create_issue_link", description="Create a link between issues.")(
    create_issue_link_tool
)
mcp.tool(name="list_issue_links", description="List links to an issue.")(
    list_issue_links_tool
)
mcp.tool(name="get_issue_link", description="Get details about an issue link.")(
    get_issue_link_tool
)
mcp.tool(name="delete_issue_link", description="Delete a link between issues.")(
    delete_issue_link_tool
)

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
mcp.tool(name="merge_merge_request", description="Merge a GitLab merge request.")(
    merge_merge_request_tool
)

# Register pipeline tools
mcp.tool(
    name="list_project_pipelines", description="List pipelines in a GitLab project."
)(list_project_pipelines_tool)
mcp.tool(
    name="get_single_pipeline",
    description="Get a single pipeline by ID for a GitLab project.",
)(get_single_pipeline_tool)
mcp.tool(
    name="get_latest_pipeline",
    description="Get the latest pipeline for the most recent commit on a specific ref.",
)(get_latest_pipeline_tool)

# Register job tools
mcp.tool(
    name="get_job",
    description="Get a specific job from a GitLab project.",
)(get_job_tool)
mcp.tool(
    name="get_job_logs",
    description="Get logs from a GitLab job.",
)(get_job_logs_tool)
mcp.tool(
    name="get_job_failure_info",
    description="Get detailed information about why a GitLab job failed, including error messages from logs.",
)(get_job_failure_info_tool)

# Register group tools
mcp.tool(name="list_groups", description="List GitLab groups.")(list_groups_tool)
mcp.tool(name="get_group", description="Get a specific GitLab group.")(get_group_tool)
mcp.tool(
    name="get_group_by_project_namespace",
    description="Get a GitLab group based on a project namespace.",
)(get_group_by_project_namespace_tool)


# Register search tools
mcp.tool(
    name="search_global",
    description="Search across all GitLab resources. Supports searching for projects, issues, merge requests, milestones, users, and more.",
)(search_global_tool)
mcp.tool(
    name="search_project",
    description="Search within a specific project. Supports searching for issues, merge requests, code content, wiki content, and more.",
)(search_project_tool)
mcp.tool(
    name="search_group",
    description="Search within a specific group. Supports searching for projects, issues, merge requests, and milestones.",
)(search_group_tool)

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
