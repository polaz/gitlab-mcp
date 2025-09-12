#!/usr/bin/env python3
"""GitLab MCP Server

A Model Context Protocol server for GitLab API with modern Work Items GraphQL support.

Authors:
    Adit pal Singh <aditpalsing@gmail.com> - Original author
    Dmitry Prudnikov <mail@polaz.com> - Work Items API implementation and enhancements

License: MIT
"""

import asyncio
import os
import threading
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

from src.schemas.search import GlobalSearchRequest, GroupSearchRequest
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
from src.services.work_item_types import initialize_work_item_types
from src.services.work_items import (
    create_work_item,
    delete_work_item,
    get_work_item,
    list_work_items,
    update_work_item,
)

# Create the MCP server
mcp = FastMCP("Gitlab", instructions="Use the tools to interact with GitLab.")

# Initialize work item types on server startup
async def init_server():
    """Initialize server components during startup."""
    try:
        type_mappings = await initialize_work_item_types()
        print(f"✅ Initialized {len(type_mappings)} work item types")
    except Exception as e:
        print(f"⚠️ Work item type initialization failed: {e}. Using fallback types.")

# Initialize server startup hook
def run_init():
    """Run async initialization in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(init_server())
    finally:
        loop.close()

# Run initialization in background thread to avoid blocking
init_thread = threading.Thread(target=run_init, daemon=True)
init_thread.start()

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


# Register work items tools (modern Work Items GraphQL API)
mcp.tool(
    name="create_work_item",
    description="""Create a new Work Item using GitLab's modern unified Work Items API (GraphQL).

🎯 NATURAL LANGUAGE MAPPING EXAMPLES:
When users ask for:
• "create a task for backend testing" → work_item_type_id="TASK", project_path="group/backend", title="Backend testing"
• "add a bug issue to frontend" → work_item_type_id="ISSUE", project_path="group/frontend", title="[Bug] ..."
• "create epic for new feature" → work_item_type_id="EPIC", namespace_path="group", title="New feature epic"
• "make a confidential task" → confidential=true, work_item_type_id="TASK"

AVAILABLE WORK ITEM TYPES (dynamically discovered):
⚡ The server automatically detects which work item types are available in your GitLab instance.
   Common types include ISSUE, EPIC, TASK, INCIDENT, TEST_CASE, REQUIREMENT, OBJECTIVE, KEY_RESULT, TICKET.

🔗 TYPE HIERARCHY & RELATIONSHIPS:
• EPIC: Top-level containers for organizing related work (Premium/Ultimate)
  - Can contain: ISSUE, TASK, INCIDENT, REQUIREMENT, TEST_CASE, OBJECTIVE
  - Use for: Major features, initiatives, product areas
  - Type names: "EPIC" (case-insensitive)
  - **SCOPE**: ALWAYS group-level only - use namespace_path, never project_path
• ISSUE: Standard work items for bugs, features, and user stories
  - Can contain: TASK, TEST_CASE, REQUIREMENT
  - Use for: Individual features, bug reports, user stories
  - Type names: "ISSUE" (case-insensitive)
• TASK: Granular work items that break down issues
  - Cannot contain other items (leaf nodes)
  - Use for: Implementation steps, subtasks, checklist items
  - Type names: "TASK" (case-insensitive)
• OBJECTIVE: High-level business goals (OKR system)
  - Can contain: KEY_RESULT
  - Use for: Business objectives, quarterly goals
  - Type names: "OBJECTIVE" (case-insensitive)
• KEY_RESULT: Measurable outcomes for objectives
  - Cannot contain other items
  - Use for: Metrics, KPIs, measurable targets
  - Type names: "KEY_RESULT", "KEY RESULT" (handles both formats)
• INCIDENT: Service disruption tracking
  - Can contain: TASK
  - Use for: Production issues, outages, service problems
  - Type names: "INCIDENT" (case-insensitive)
• TEST_CASE: Quality assurance work items
  - Cannot contain other items
  - Use for: Test scenarios, QA verification steps
  - Type names: "TEST_CASE", "TEST CASE" (handles both formats)
• REQUIREMENT: Product/business requirements
  - Can contain: TEST_CASE, TASK
  - Use for: Specifications, acceptance criteria
  - Type names: "REQUIREMENT" (case-insensitive)
• TICKET: General purpose work items
  - Similar to ISSUE but for different organizational contexts
  - Type names: "TICKET" (case-insensitive)

REQUIRED FIELDS:
- work_item_type_id: Work item type identifier - can be either:
  * Type NAME (e.g., "ISSUE", "TASK", "EPIC") - automatically resolved via dynamic discovery
  * Global ID (e.g., "gid://gitlab/WorkItems::Type/2") - direct GitLab identifier

⚡ DYNAMIC TYPE DISCOVERY: The server automatically discovers available work item types from your GitLab instance on startup, eliminating the need for hardcoded type mappings.

- title: Descriptive title for the work item
- project_path OR namespace_path: Context location

CURRENTLY SUPPORTED FIELDS:
- title: Work item title (required)
- description: Markdown description (optional)
- confidential: Privacy setting (optional)

WIDGET SUPPORT STATUS:
⚠️ CURRENT LIMITATION: Advanced widget operations are not yet implemented in create_work_item.
The following features are planned for future enhancement:

PLANNED WIDGET CAPABILITIES:
- Hierarchy: Parent/child relationships between work items
- Assignees: Users responsible for the work
- Labels: Categorization and filtering tags
  ⚠️ IMPORTANT: Agents should ONLY use labels that already exist in the project/group scope.
  Use list_labels or search functions to discover existing labels before assigning them.
  Creating new labels should be done explicitly through separate label management functions after user approval.
- Milestone: Release/sprint association
- Iteration: Sprint/iteration assignment (Premium/Ultimate)
- Health Status: On track/needs attention/at risk
- Progress: Percentage completion
- Weight: Story points or complexity estimation
- Start/Due Dates: Timeline planning

CURRENT WORKFLOW:
1. Create basic work item with create_work_item (title, description, confidential)
2. Use update_work_item for advanced widget operations (when implemented)
3. Use get_work_item to inspect created work item with all widgets

COMMON USAGE PATTERNS:
1. Epic → Issues → Tasks (hierarchical planning)
2. Objective → Key Results (OKR tracking)
3. Incident → Tasks (incident response)
4. Requirement → Test Cases (quality assurance)""",
)(create_work_item)

mcp.tool(
    name="list_work_items",
    description="""⚡ USE THIS TO LIST ALL ISSUES/TASKS/EPICS IN A PROJECT WITHOUT REQUIRING SEARCH TERMS

List Work Items from a project or group using GitLab's modern Work Items API (GraphQL).
Unlike search tools, this can retrieve ALL work items without any search query required.

🎯 CRITICAL USAGE PATTERNS:
✅ "find all issues in project X" → list_work_items(project_path="X")
✅ "show open bugs in project Y" → list_work_items(project_path="Y", search="bug", state="OPENED")
✅ "list tasks in backend" → list_work_items(project_path="group/backend", work_item_types=["TASK"])
✅ "get epics from team" → list_work_items(namespace_path="team", work_item_types=["EPIC"])
✅ "what's in the backlog" → list_work_items(state="OPENED", work_item_types=["ISSUE", "TASK"])
❌ "find all issues in project X" → search_project() [WRONG - requires search term]

🎯 NATURAL LANGUAGE MAPPING EXAMPLES:
When users ask for:
• "show tasks from backend" → project_path="group/backend", work_item_types=["TASK"]
• "list issues in frontend project" → project_path="group/frontend", work_item_types=["ISSUE"]
• "get epics from team" → namespace_path="team", work_item_types=["EPIC"]
• "show open items" → state="OPENED" (omit work_item_types for all types)
• "find bugs in project" → search="bug" (searches titles and descriptions)
• "show tasks and issues" → work_item_types=["TASK", "ISSUE"]
• "what's in the backlog" → state="OPENED", work_item_types=["ISSUE", "TASK"]

SCOPE OPTIONS:
- project_path: List work items within a specific project (e.g., "mygroup/backend")
- namespace_path: List work items within a group/namespace (includes subgroups)

FILTERING CAPABILITIES:
- work_item_types: Filter by specific types using dynamic discovery
  * Use type NAMES (e.g., ["ISSUE", "TASK", "EPIC"]) - case-insensitive
  * Or use global IDs (e.g., ["gid://gitlab/WorkItems::Type/2"])
  * Multiple types can be specified as array
  * Omit to return all types

⚡ DYNAMIC TYPES: The server automatically discovers available work item types from your GitLab instance, so you can use the actual type names without worrying about instance-specific IDs.
- state: Filter by work item state
  * OPENED: Active work items
  * CLOSED: Completed work items
  * ALL: Both open and closed
- search: Text search across titles and descriptions
  * Searches work item titles and content
  * Supports partial matching
- first: Pagination limit (default 50, max 100)
- after: Pagination cursor for subsequent pages

RETURNED INFORMATION:
- Basic identifiers: id, iid, title, state
- Work item type information
- Author details and creation/update timestamps
- Direct web URLs for GitLab navigation
- Pagination info for large result sets

COMMON USE CASES:
1. Project planning: List all epics in a group
2. Sprint management: List open issues in a project
3. Task tracking: List tasks under specific parent items
4. Incident response: List open incidents across organization
5. OKR tracking: List objectives and key results
6. Quality assurance: List test cases for testing cycles

PERFORMANCE NOTES:
- Group-level queries may return large result sets
- Use pagination (first/after) for better performance
- Consider filtering by type and state to reduce results""",
)(list_work_items)

mcp.tool(
    name="get_work_item",
    description="""Get detailed information for a specific Work Item using GitLab's modern Work Items API (GraphQL).

🎯 NATURAL LANGUAGE MAPPING EXAMPLES:
When users ask for:
• "show me issue #42" → iid=42, project_path="group/project"
• "get details of task 123" → iid=123, project_path="group/project"
• "inspect this work item" → id="gid://gitlab/WorkItem/456" (from previous API call)
• "tell me about epic #5" → iid=5, project_path="group/project"

IDENTIFICATION OPTIONS (choose one):
- id: Global Work Item ID (format: gid://gitlab/WorkItem/123)
  * Use for direct work item access across projects
  * Obtained from other API responses or GitLab UI
- iid + project_path: Internal ID within specific project
  * iid: Sequential number within project (e.g., #42)
  * project_path: Full project path (e.g., 'group/project')

⚡ DYNAMIC TYPE INFORMATION: The returned work item includes discovered type information with both the global type ID and human-readable type name, thanks to the server's dynamic type discovery.

RETURNED COMPREHENSIVE DATA:
Core Information:
- Identifiers: id, iid, title, state, confidential status
- Metadata: creation/update/close timestamps, web URL, reference
- Author information and project/namespace context
- Work item type details

Widget-Based Data (varies by type):
• Hierarchy Widget:
  - parent: Direct parent work item (if any)
  - children: List of child work items with types
  - Enables navigation of work item trees

• Assignees Widget:
  - assignees: List of users assigned to this work item
  - User details: name, username, profile URLs

• Labels Widget:
  - labels: Categorization tags with colors and descriptions
  - Used for filtering, reporting, and organization

• Milestone Widget:
  - milestone: Associated release/sprint milestone
  - Planning and timeline context

• Iteration Widget (Premium/Ultimate):
  - iteration: Current sprint/iteration assignment
  - Agile development context

• Description Widget:
  - description: Full markdown content
  - descriptionHtml: Rendered HTML version

• Dates Widget:
  - startDate: Planned start date
  - dueDate: Target completion date

• Progress Widget:
  - progress: Percentage completion (0-100)

• Health Status Widget:
  - healthStatus: ON_TRACK, NEEDS_ATTENTION, AT_RISK

• Weight Widget:
  - weight: Story points or complexity estimation

COMMON USE CASES:
1. Detailed work item inspection before updates
2. Understanding work item relationships and hierarchy
3. Extracting assignee and label information
4. Progress tracking and status monitoring
5. Planning with dates and milestones
6. Quality assurance and testing workflows""",
)(get_work_item)

mcp.tool(
    name="update_work_item",
    description="""Update a Work Item using GitLab's modern Work Items API (GraphQL).

REQUIRED IDENTIFICATION:
- id: Global Work Item ID (format: gid://gitlab/WorkItem/123)
  * Must be obtained from get_work_item or list_work_items responses

BASIC FIELD UPDATES:
- title: Change work item title
- confidential: Set confidentiality (true/false)
- state_event: Change work item state
  * 'reopen': Reopen a closed work item
  * 'close': Close an open work item

WIDGET-BASED UPDATES (available via GraphQL mutations):
⚠️ Note: Advanced widget operations are currently limited in this implementation
Future enhancements will include full widget manipulation:

Planned Widget Operations:
• Hierarchy Management:
  - Set parent work item relationships
  - Add/remove child work items
  - Reorder children within hierarchy

• Assignee Management:
  - Assign users to work items
  - Remove assignees
  - Replace entire assignee list

• Label Management:
  - Add labels to work items
  - Remove specific labels
  - Replace all labels at once

• Milestone/Iteration Assignment:
  - Set milestone for release planning
  - Assign to iteration for sprint management
  - Clear milestone/iteration assignments

• Progress Tracking:
  - Update progress percentage
  - Set health status indicators
  - Update weight/story points

• Timeline Management:
  - Set start and due dates
  - Clear date assignments
  - Schedule work items

CURRENT CAPABILITIES:
- Basic field updates (title, state, confidential)
- State transitions (open/close)
- Work item property modifications

PLANNED ENHANCEMENTS:
Widget-based operations will be added in future updates to support:
- Complete assignee management
- Comprehensive label operations
- Hierarchy relationship management
- Progress and timeline updates

COMMON UPDATE PATTERNS:
1. State management: Open/close work items
2. Title updates: Refine work item descriptions
3. Confidentiality: Control access to sensitive work items""",
)(update_work_item)

mcp.tool(
    name="delete_work_item",
    description="""Delete a Work Item using GitLab's modern Work Items API (GraphQL).

⚠️ CRITICAL WARNING: This operation is PERMANENT and IRREVERSIBLE!

REQUIRED IDENTIFICATION:
- id: Global Work Item ID (format: gid://gitlab/WorkItem/123)
  * Must be obtained from get_work_item or list_work_items responses
  * Verify the correct work item before deletion

DELETION IMPACT BY TYPE:

• EPIC Deletion:
  - Removes the epic container permanently
  - Child work items (issues, tasks) become orphaned but remain
  - Epic-child relationships are severed
  - All epic-specific data (description, labels, etc.) lost forever
  - Consider reassigning children to another epic first

• ISSUE Deletion:
  - Removes issue and all associated data permanently
  - Child tasks become orphaned but remain
  - All comments, assignees, labels, and metadata lost
  - Issue references in code/commits become broken links
  - Consider closing instead of deleting for historical tracking

• TASK Deletion:
  - Removes task work item permanently
  - Parent-child relationship automatically updated
  - All task progress and data lost forever
  - Least risky deletion as tasks are typically granular

• OBJECTIVE/KEY_RESULT Deletion:
  - Removes OKR tracking data permanently
  - Breaks objective-key result relationships
  - All progress and measurement data lost
  - Impact on business goal tracking

• INCIDENT Deletion:
  - Removes incident tracking permanently
  - Child tasks become orphaned
  - All incident response data and timeline lost
  - Not recommended for completed incidents (close instead)

• TEST_CASE/REQUIREMENT Deletion:
  - Removes quality assurance data permanently
  - Breaks requirement-test relationships
  - All testing history and results lost

PERMISSION REQUIREMENTS:
- Must have appropriate permissions for the project/group
- Only work item authors, assignees, and project maintainers can delete
- Some organizations may restrict deletion permissions

SAFE DELETION PRACTICES:
1. Always use get_work_item first to verify correct item
2. Check for child work items and reassign if needed
3. Consider closing instead of deleting for auditability
4. Export important data before deletion
5. Verify no critical references exist in code or documentation

ALTERNATIVE TO DELETION:
- Close work items instead to maintain historical records
- Use confidential setting to hide sensitive work items
- Archive projects to remove from active view while preserving data""",
)(delete_work_item)

# Wrapper functions for search tools to handle MCP input model format
async def search_globally_wrapper(input_model: GlobalSearchRequest):
    """Wrapper for search_globally to handle MCP input model format."""
    return await search_globally(input_model.search, input_model.scope)

async def search_group_wrapper(input_model: GroupSearchRequest):
    """Wrapper for search_group to handle MCP input model format."""
    return await search_group(input_model.group_id, input_model.search, input_model.scope)

# Register search tools
mcp.tool(
    name="search_project",
    description="""⚠️ REQUIRES A SEARCH TERM - Cannot list all issues. Use list_work_items to get all issues.

Search within a specific GitLab project for SPECIFIC KEYWORDS in content.

🎯 CRITICAL USAGE PATTERNS:
✅ "find issues mentioning authentication in project X" → search_project(project_id="X", scope="issues", search="authentication")
✅ "search for TODO comments in code" → search_project(project_id="X", scope="blobs", search="TODO")
❌ "find all issues in project X" → Use list_work_items(project_path="X") instead
❌ "list all open issues" → Use list_work_items(project_path="X", state="OPENED") instead

WHEN TO USE search_project vs list_work_items:
- search_project: When searching for SPECIFIC KEYWORDS in issue content
- list_work_items: When listing ALL issues/tasks/epics (no search term needed)

IMPORTANT: Each search call targets ONE specific scope/content type. To search multiple types, make separate calls for each scope.

SUPPORTED SEARCH SCOPES (choose one per call):
- 'projects': Project metadata (name, description, topics)
- 'blobs': File contents within repository code
- 'wiki_blobs': Wiki page contents and documentation
- 'issues': Issue titles and descriptions
- 'merge_requests': Merge request titles and descriptions
- 'commits': Commit messages and metadata
- 'milestones': Milestone titles and descriptions
- 'notes': Comments on issues and merge requests

MULTI-TYPE SEARCH STRATEGY:
To search across multiple content types (e.g., both issues AND merge requests):
1. Make separate search_project calls for each scope
2. Use same search term with different scope parameters
3. Combine results programmatically for comprehensive coverage

EXAMPLE MULTI-SCOPE USAGE:
- Call 1: search_project(project_id="my/project", scope="issues", search="authentication")
- Call 2: search_project(project_id="my/project", scope="merge_requests", search="authentication")
- Call 3: search_project(project_id="my/project", scope="blobs", search="authentication")

REQUIREMENTS:
- project_id: Project path (e.g., 'group/project') or numeric ID
- scope: Single content type from list above
- search: Search term (minimum 1 character, REQUIRED - cannot be empty)
- ref: Optional branch/tag for blob and commit searches""",
)(search_project)
mcp.tool(
    name="search_globally",
    description="""Search across ALL GitLab content you have access to.

IMPORTANT: Each search call targets ONE specific scope/content type. To search multiple types, make separate calls for each scope.

SUPPORTED SEARCH SCOPES (choose one per call):
- 'projects': Project metadata across all accessible projects
- 'blobs': File contents across all repositories (requires Premium/Ultimate)
- 'wiki_blobs': Wiki page contents across all project wikis
- 'issues': Issue titles and descriptions across all projects
- 'merge_requests': Merge request titles and descriptions across all projects
- 'commits': Commit messages and metadata across all repositories
- 'milestones': Milestone titles and descriptions across all projects
- 'notes': Comments on issues and merge requests across all projects

MULTI-TYPE SEARCH STRATEGY:
To search across multiple content types globally (e.g., issues AND merge requests across all projects):
1. Make separate search_globally calls for each scope
2. Use same search term with different scope parameters
3. Combine results programmatically for comprehensive coverage

EXAMPLE MULTI-SCOPE USAGE:
- Call 1: search_globally(scope="issues", search="authentication bug")
- Call 2: search_globally(scope="merge_requests", search="authentication bug")
- Call 3: search_globally(scope="blobs", search="authentication bug")

SCOPE COVERAGE:
- Most comprehensive search across all accessible GitLab content
- Includes public projects and private projects where you're a member
- Results limited by your GitLab permissions and instance search limits
- Blob search may require Premium/Ultimate subscription

REQUIREMENTS:
- scope: Single content type from list above
- search: Search term (minimum 3 characters, no wildcards like '*')

PERFORMANCE CONSIDERATIONS:
- Global searches may return large result sets
- Consider using search_group or search_project for more targeted results
- Some scopes (like blobs) may have additional subscription requirements""",
)(search_globally_wrapper)
mcp.tool(
    name="search_group",
    description="""Search within a specific GitLab group and its projects/subgroups.

IMPORTANT: Each search call targets ONE specific scope/content type. To search multiple types, make separate calls for each scope.

SUPPORTED SEARCH SCOPES (choose one per call):
- 'projects': Project metadata within the group and subgroups
- 'blobs': File contents within group repositories
- 'wiki_blobs': Wiki page contents within group projects
- 'issues': Issue titles and descriptions within group projects
- 'merge_requests': Merge request titles and descriptions within group projects
- 'commits': Commit messages and metadata within group repositories
- 'milestones': Milestone titles and descriptions within group projects
- 'notes': Comments on issues and merge requests within group projects

MULTI-TYPE SEARCH STRATEGY:
To search across multiple content types within a group (e.g., issues AND merge requests):
1. Make separate search_group calls for each scope
2. Use same search term with different scope parameters
3. Combine results programmatically for comprehensive coverage

EXAMPLE MULTI-SCOPE USAGE:
- Call 1: search_group(group_id="my-team", scope="issues", search="bug fix")
- Call 2: search_group(group_id="my-team", scope="merge_requests", search="bug fix")
- Call 3: search_group(group_id="my-team", scope="commits", search="bug fix")

SCOPE BENEFITS:
- More focused than global search, faster results
- Searches group and all subgroups/projects
- Better performance for large GitLab instances
- Group-specific permission handling

REQUIREMENTS:
- group_id: Group path (e.g., 'my-team') or numeric ID
- scope: Single content type from list above
- search: Search term (minimum 3 characters, no wildcards like '*')

PERFORMANCE NOTES:
- Faster than global search due to reduced scope
- Results include all subgroups and their projects
- Group permissions determine result visibility""",
)(search_group_wrapper)


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
