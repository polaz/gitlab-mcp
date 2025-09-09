import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback manual loading if python-dotenv not available
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with env_file.open() as f:
            for line_content in f:
                line = line_content.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

from mcp.server.fastmcp import FastMCP

from src.services.branches import (
    create_branch,
    delete_branch,
    delete_merged_branches,
    get_branch,
    get_default_branch_ref,
    list_branches,
    protect_branch,
    unprotect_branch,
)
from src.services.epics import (
    assign_issue_to_epic,
    create_epic,
    delete_epic,
    get_epic,
    list_epic_issues,
    list_epics,
    remove_issue_from_epic,
    update_epic,
    update_epic_issue_association,
)
from src.services.files import (
    create_file,
    delete_file,
    get_file_contents,
    update_file,
)
from src.services.groups import (
    get_group,
    get_group_by_project_namespace,
    list_groups,
)
from src.services.issues import (
    close_issue,
    comment_on_issue,
    create_issue,
    delete_issue,
    get_issue,
    list_all_issues,
    list_issue_comments,
    move_issue,
    update_issue,
)
from src.services.jobs import (
    get_job_logs,
)
from src.services.merge_requests import (
    create_merge_request,
    create_merge_request_comment,
    delete_merge_request,
    get_merge_request,
    list_merge_requests,
    merge_merge_request,
    merge_request_changes,
    update_merge_request,
)
from src.services.repositories import create_repository, list_repository_tree
from src.services.search import search_globally, search_group, search_project

# Create the MCP server
mcp = FastMCP("Gitlab", instructions="Use the tools to interact with GitLab.")

# Register repository tools

mcp.tool(name="create_repository", description="Create a new GitLab repository.")(
    create_repository
)
mcp.tool(
    name="list_repository_tree",
    description="List files and directories in a GitLab repository.",
)(list_repository_tree)


# Register branch tools
mcp.tool(
    name="create_branch", description="Create a new branch in a GitLab repository."
)(create_branch)
mcp.tool(
    name="get_default_branch_ref",
    description="Get the default branch reference for a GitLab repository.",
)(get_default_branch_ref)
mcp.tool(
    name="list_branches",
    description="List branches in a GitLab repository.",
)(list_branches)
mcp.tool(
    name="get_branch",
    description="Get details for a specific GitLab branch.",
)(get_branch)
mcp.tool(
    name="delete_branch",
    description="Delete a branch from a GitLab repository.",
)(delete_branch)
mcp.tool(
    name="delete_merged_branches",
    description="Delete all merged branches from a GitLab repository.",
)(delete_merged_branches)
mcp.tool(
    name="protect_branch",
    description="Protect a branch in a GitLab repository.",
)(protect_branch)
mcp.tool(
    name="unprotect_branch",
    description="Remove protection from a branch in a GitLab repository.",
)(unprotect_branch)

# Register file tools

mcp.tool(
    name="create_file",
    description="Create a new file in a GitLab repository.",
)(create_file)
mcp.tool(
    name="get_file_contents",
    description="Retrieve the contents of a file from a GitLab repository.",
)(get_file_contents)

mcp.tool(
    name="update_file",
    description="Update an existing file in a GitLab repository.",
)(update_file)
mcp.tool(
    name="delete_file",
    description="Delete a file from a GitLab repository.",
)(delete_file)

# Register issue tools
mcp.tool(
    name="create_issue",
    description="Create a new issue in a GitLab repository with comprehensive field support. IMPORTANT: Use epic_id or epic_iid fields to link issues to epics, NOT description text. Supports assignees, milestones, due dates, labels, weight, issue type, and confidentiality settings. Perfect for creating well-structured issues with proper epic relationships and project metadata."
)(create_issue)

mcp.tool(
    name="list_all_issues",
    description="List all issues the authenticated user has access to.",
)(list_all_issues)

mcp.tool(name="get_issue", description="Get details for a specific GitLab issue.")(
    get_issue
)
mcp.tool(name="close_issue", description="Close a GitLab issue.")(close_issue)
mcp.tool(
    name="update_issue",
    description="Update an existing issue in a GitLab repository with comprehensive field support including assignees, labels, state, and metadata."
)(update_issue)
mcp.tool(name="delete_issue", description="Delete an issue from a GitLab repository.")(
    delete_issue
)
mcp.tool(name="move_issue", description="Move an issue to a different project.")(
    move_issue
)
mcp.tool(name="comment_on_issue", description="Add a comment to a GitLab issue.")(
    comment_on_issue
)

mcp.tool(
    name="list_issue_comments",
    description="List comments on a specific GitLab issue.",
)(list_issue_comments)

# Register merge request tools
mcp.tool(
    name="create_merge_request",
    description="Create a new merge request in a GitLab repository.",
)(create_merge_request)
mcp.tool(
    name="list_merge_requests", description="List merge requests for a GitLab project."
)(list_merge_requests)
mcp.tool(
    name="get_merge_request",
    description="Get details for a specific GitLab merge request.",
)(get_merge_request)
mcp.tool(name="merge_merge_request", description="Merge a GitLab merge request.")(
    merge_merge_request
)
mcp.tool(
    name="update_merge_request",
    description="Update an existing merge request in GitLab.",
)(update_merge_request)
mcp.tool(
    name="delete_merge_request",
    description="Delete a merge request from a GitLab repository.",
)(delete_merge_request)
mcp.tool(
    name="merge_request_changes", description="Get the changes for a merge request."
)(merge_request_changes)
mcp.tool(
    name="create_merge_request_comment", description="Add a comment to a merge request."
)(create_merge_request_comment)

# Register job tools

mcp.tool(
    name="get_job_logs",
    description="Get logs from a GitLab job.",
)(get_job_logs)


# Register group tools
mcp.tool(name="list_groups", description="List GitLab groups.")(list_groups)
mcp.tool(name="get_group", description="Get a specific GitLab group.")(get_group)
mcp.tool(
    name="get_group_by_project_namespace",
    description="Get a GitLab group based on a project namespace.",
)(get_group_by_project_namespace)


# Register search tools
mcp.tool(
    name="search_project",
    description="Search for file contents (blobs), wiki content, and project metadata within a specific GitLab project. IMPORTANT: Does NOT search issues, merge requests, or other GitLab objects. For project issues, use list_all_issues with the project_path parameter. Requires specific search terms (not wildcards like '*').",
)(search_project)
mcp.tool(
    name="search_globally",
    description="Search for projects, file contents (blobs), and wiki content across all GitLab instances you have access to. IMPORTANT: Does NOT search issues, merge requests, or other GitLab objects. For issues, use list_all_issues without project_path for global search. Requires specific search terms (not wildcards like '*').",
)(search_globally)
mcp.tool(
    name="search_group",
    description="Search for projects, file contents (blobs), and wiki content within a specific GitLab group. IMPORTANT: Does NOT search issues, merge requests, or other GitLab objects. For issues, use list_all_issues with project_path parameter. Requires specific search terms (not wildcards like '*'). Only searches projects, blobs, and wiki_blobs scopes.",
)(search_group)

# Register epic tools
mcp.tool(
    name="create_epic",
    description="Create a new epic in a GitLab group. Epics are high-level containers for organizing related issues and child epics, available in GitLab Premium/Ultimate. Supports title, description, labels, dates, confidentiality, parent epic hierarchy, and visual organization with colors. Perfect for project planning, feature grouping, and milestone tracking.",
)(create_epic)

mcp.tool(
    name="list_epics",
    description="List epics in a GitLab group with comprehensive filtering. Filter by state (opened/closed), labels, author, search terms, date ranges, and hierarchy options. Supports pagination and includes ancestor/descendant group searching. Essential for epic discovery, project overview, and team planning workflows.",
)(list_epics)

mcp.tool(
    name="get_epic",
    description="Get detailed information for a specific epic in a GitLab group. Retrieves complete epic metadata including title, description, state, dates, labels, author, hierarchy relationships, and visual settings. Use this to examine epic details before updates or to display epic information in workflows.",
)(get_epic)

mcp.tool(
    name="update_epic",
    description="Update an existing epic in a GitLab group with comprehensive field support. Modify title, description, state (close/reopen), dates, confidentiality, parent relationships, and visual properties. Advanced label management with add/remove operations. Ideal for epic maintenance, status updates, and project reorganization.",
)(update_epic)

mcp.tool(
    name="delete_epic",
    description="Permanently delete an epic from a GitLab group. WARNING: This action cannot be undone and will remove all epic-issue associations (issues remain in projects). Use with caution for cleaning up obsolete epics or project restructuring. Requires appropriate permissions.",
)(delete_epic)

mcp.tool(
    name="list_epic_issues",
    description="List all issues currently assigned to a specific epic. Shows issue details with association metadata for project tracking and epic content overview. Essential for understanding epic scope, progress monitoring, and issue organization within epics.",
)(list_epic_issues)

mcp.tool(
    name="assign_issue_to_epic",
    description="Assign an issue to an epic, creating a relationship between them. If the issue was previously assigned to another epic, it will be reassigned. Use the global issue ID (not issue_iid). Perfect for organizing issues under epics, project planning, and feature grouping workflows.",
)(assign_issue_to_epic)

mcp.tool(
    name="remove_issue_from_epic",
    description="Remove an issue from an epic, breaking their association. The issue remains in its project but is no longer part of the epic. Requires the epic-issue association ID (get from list_epic_issues). Useful for epic reorganization and issue management.",
)(remove_issue_from_epic)

mcp.tool(
    name="update_epic_issue_association",
    description="Update the position/order of an issue within an epic's issue list. Reorder issues by moving before or after other issues for prioritization and organization. Use association IDs from list_epic_issues. Essential for epic planning and issue prioritization workflows.",
)(update_epic_issue_association)

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
