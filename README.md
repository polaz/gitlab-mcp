# GitLab MCP Server

A MCP (Model Context Protocol) server for interacting with GitLab API using the modern Work Items GraphQL API. This server provides comprehensive tools for managing GitLab work items (epics, issues, tasks), repositories, merge requests, and more with enhanced agentic support.

## Installation

### Quick Start (No Installation Required)

**Requirements:** Only [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

Run directly from GitHub without cloning or installing:

```bash
uv run --python 3.13 --with git+https://github.com/polaz/gitlab-mcp.git python -m gitlab_mcp
```

### Using uv (Local Development)

```bash
# Clone the repository
git clone https://github.com/polaz/gitlab-mcp.git
cd gitlab-mcp

# Install dependencies using uv
uv sync
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/polaz/gitlab-mcp.git
cd gitlab-mcp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

The GitLab MCP server requires environment variables for configuration:

### Required Variables

1. `GITLAB_PERSONAL_ACCESS_TOKEN` - For authentication with GitLab API (both REST and GraphQL)
2. `GITLAB_API_URL` - The base URL for the GitLab API (automatically used for both `/api/v4` REST and `/api/graphql` GraphQL endpoints)


### Option 1: Environment Variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Example `.env` file:

```
GITLAB_PERSONAL_ACCESS_TOKEN=your_personal_access_token
GITLAB_API_URL=https://gitlab.com
```

### Option 2: MCP Client Configuration (Recommended)

Add to your MCP client configuration (e.g., Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gitlab-mcp": {
      "command": "uv",
      "args": ["run", "--python", "3.13", "--with", "git+https://github.com/polaz/gitlab-mcp.git", "python", "-m", "gitlab_mcp"],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "your_personal_access_token",
        "GITLAB_API_URL": "https://gitlab.com"
      }
    }
  }
}
```

**Requirements:** Only [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager - no cloning or installation needed!
## Project Structure

The project follows a modular, domain-driven architecture:

```
gitlab-mcp/
├── src/                           # Source code
│   ├── api/                       # API interaction layer
│   │   ├── rest_client.py         # GitLab REST API client
│   │   ├── graphql_client.py      # GitLab GraphQL API client (Work Items)
│   │   ├── exceptions.py          # API exception definitions
│   ├── schemas/                   # Data models and validation
│   │   ├── base.py                # Base schema classes
│   │   ├── repositories.py        # Repository data models
│   │   ├── branches.py            # Branch data models
│   │   ├── work_items.py          # Work Items data models (GraphQL)
│   │   ├── merge_requests.py      # Merge request data models
│   │   ├── milestones.py          # Milestone data models (UX optimized)
│   │   ├── iterations.py          # Iteration data models
│   │   ├── groups.py              # Group data models
│   │   ├── labels.py              # Label data models
│   │   └── search.py              # Search data models (enhanced with contextual fields)
│   ├── services/                  # Business logic layer
│   │   ├── repositories.py        # Repository operations
│   │   ├── branches.py            # Branch operations
│   │   ├── work_items.py          # Work Items operations (GraphQL)
│   │   ├── merge_requests.py      # Merge request operations
│   │   ├── milestones.py          # Milestone operations
│   │   ├── iterations.py          # Iteration operations
│   │   ├── groups.py              # Group operations
│   │   ├── labels.py              # Label operations
│   │   └── search.py              # Search operations
├── server.py                      # Main MCP server entry point
```

This architecture provides several benefits:

- **Separation of concerns**: Each module has a clear responsibility
- **Type safety**: Pydantic schemas ensure data validation
- **Maintainability**: Domain-driven organization makes code easier to navigate
- **Extensibility**: New features can be added by following the established patterns
- **Async support**: All operations are available in both synchronous and asynchronous versions

## Available Tools

The server provides the following tools for interacting with GitLab:

### Repository Management

- `create_repository`: Create a new GitLab repository
- `list_repository_tree`: List the contents of a repository tree

### Branch Operations

- `create_branch`: Create a new branch in a GitLab repository
- `list_branches`: List branches in a GitLab repository
- `get_branch`: Get details for a specific GitLab branch
- `delete_branch`: Delete a branch from a GitLab repository
- `delete_merged_branches`: Delete all merged branches from a GitLab repository
- `protect_branch`: Protect a branch in a GitLab repository
- `unprotect_branch`: Remove protection from a branch in a GitLab repository
- `get_default_branch_ref`: Get the default branch reference for a GitLab repository

### File Operations

- `create_file`: Create a new file in a GitLab repository
- `get_file_contents`: Retrieve the contents of a file from a GitLab repository
- `update_file`: Update an existing file in a GitLab repository
- `delete_file`: Delete a file from a GitLab repository


### Merge Request Operations

- `create_merge_request`: Create a new merge request in a GitLab repository
- `list_merge_requests`: List merge requests for a GitLab project
- `get_merge_request`: Get details for a specific GitLab merge request
- `merge_merge_request`: Merge a GitLab merge request
- `update_merge_request`: Update an existing merge request in a GitLab repository.
- `delete_merge_request`: Delete a merge request from a GitLab repository.
- `merge_request_changes`: Get the changes for a specific merge request.
- `create_merge_request_comment`: Add a comment to a GitLab merge request.

### Job Operations

- `get_job_logs`: Get logs from a GitLab job

### Group Operations

- `list_groups`: List GitLab groups
- `get_group`: Get a specific GitLab group
- `get_group_by_project_namespace`: Get a GitLab group based on a project namespace

### Search Tools

- `search_globally`: Search across ALL GitLab content you have access to, supporting multiple scopes: 'projects' (metadata), 'blobs' (file contents), 'wiki_blobs' (wiki pages), 'issues' (titles/descriptions), 'merge_requests' (titles/descriptions), 'commits' (messages/content), 'milestones', and 'notes' (comments). Enhanced with additional contextual fields including project namespaces, group information, labels, assignees, and other valuable metadata.
- `search_project`: Search within a specific GitLab project across all content types. Supports all scopes mentioned above and perfect for finding specific content within a project. Enhanced with detailed context information.
- `search_group`: Search within a specific GitLab group and its projects/subgroups across all content types. More focused than global search with faster results and comprehensive contextual fields.


### Work Items Operations (Modern GraphQL API) ⭐

**🚀 PRIMARY API**: GitLab's unified Work Items API replaces deprecated epic/issue REST endpoints with enhanced functionality and comprehensive agentic support.

- **`create_work_item`**: **🚀 ENHANCED WITH FULL WIDGET SUPPORT** - Create epics, issues, tasks, objectives, incidents, test cases, and requirements with complete widget operations (labels, assignees, hierarchy, milestones, dates) during creation. One-step work item creation with comprehensive agentic guidance.

- **`list_work_items`**: Advanced filtering by type, state, search terms with project/group scope support. Comprehensive pagination and performance guidance for optimal agentic workflow management.

- **`get_work_item`**: Complete work item retrieval with all 19 widget types (assignees, hierarchy, labels, milestones, iterations, dates, descriptions, progress, health status, weight, and more). Supports both global ID and IID+project access methods.

- **`update_work_item`**: Advanced widget operations for comprehensive work item management including:
  - **Assignee Management**: Add/remove user assignments with structured operations
  - **Label Operations**: Add and remove labels with granular control
  - **Hierarchy Management**: Set parent-child relationships between work items
  - **Milestone Assignment**: Associate or clear milestone assignments
  - **Iteration Assignment**: Sprint/iteration management (Premium/Ultimate)
  - **Date Management**: Set start and due dates with validation
  - **State Transitions**: Open/close work items with proper state management
  - **Confidentiality Control**: Toggle confidential status
  - **Title Updates**: Modify work item titles with validation

- **`delete_work_item`**: Permanent deletion with comprehensive safety warnings, verification procedures, and detailed impact documentation by work item type for responsible agentic operations.

**✅ VERIFIED**: All functions thoroughly tested against live GitLab API.

#### Widget Operations in Work Items

GitLab Work Items use a widget-based architecture where functionality is provided through specialized widgets. This MCP server implements structured widget operations for comprehensive work item management:

**Available Widget Operations:**

- **Assignees Widget** (`AssigneeWidgetOperation`):
  - Assign multiple users to work items using GitLab user IDs
  - Format: `gid://gitlab/User/123`

- **Labels Widget** (`LabelWidgetOperation`):
  - Add specific labels: `add_label_ids: ["gid://gitlab/ProjectLabel/456"]`
  - Remove specific labels: `remove_label_ids: ["gid://gitlab/ProjectLabel/789"]`
  - Granular control over label modifications

- **Hierarchy Widget** (`HierarchyWidgetOperation`):
  - Set parent-child relationships: `parent_id: "gid://gitlab/WorkItem/123"`
  - Clear relationships: `parent_id: null`
  - Enable epic → issue → task hierarchies

- **Milestone Widget** (`MilestoneWidgetOperation`):
  - Associate with milestones: `milestone_id: "gid://gitlab/Milestone/456"`
  - Clear assignments: `milestone_id: null`

- **Iteration Widget** (`IterationWidgetOperation`):
  - Sprint management: `iteration_id: "gid://gitlab/Iteration/789"`
  - Clear assignments: `iteration_id: null`
  - Requires Premium/Ultimate tier

- **Dates Widget** (`DatesWidgetOperation`):
  - Set dates: `start_date: "2024-01-15", due_date: "2024-02-15"`
  - Clear dates: `start_date: null, due_date: null`
  - ISO date format validation

**Type Safety:** All widget operations use Pydantic schemas for validation, ensuring proper data types and preventing API errors before requests are sent to GitLab.

### Milestone Operations

- `create_milestone`: Create a new milestone in a GitLab project or group for organizing issues and merge requests by releases, sprints, or goals
- `list_milestones`: List milestones in a GitLab project or group with filtering by state and search terms for project planning
- `get_milestone`: Get detailed information for a specific milestone including dates, state, and associated metadata
- `update_milestone`: Update an existing milestone in GitLab including title, description, dates, and state changes
- `delete_milestone`: Permanently delete a milestone from a GitLab project or group

### Iteration Operations (Premium/Ultimate)

**Note**: Individual iteration creation via REST API is not supported by GitLab. Iterations are managed through iteration cadences (automated scheduling) in the GitLab UI or via GraphQL Work Items API.

- `list_iterations`: List iterations in a GitLab group with filtering by state and search terms for agile project management
- `get_iteration`: Get detailed information for a specific iteration including dates, state, and sequence number
- `update_iteration`: Update an existing iteration in GitLab including title, description, dates, and state changes
- `delete_iteration`: Permanently delete an iteration from a GitLab group

### Label Management (Via Work Items API) ⭐

**🚀 PRIMARY LABEL MANAGEMENT**: Labels are now managed through the modern Work Items API for comprehensive integration:

- **`create_work_item`** with `labels_widget`: Create work items with labels during creation
- **`update_work_item`** with `labels_widget`: Add/remove labels from existing work items  
- **`get_work_item`**: View current labels on work items with full label details
- **`search_project`**: Discover existing labels by searching for label usage patterns

**🎯 AGENT-OPTIMIZED WORKFLOW**:
1. **Discovery**: Use search tools to find existing labels before creating work items
2. **Creation**: Use `create_work_item` with `labels_widget` for new work items with labels
3. **Updates**: Use `update_work_item` with `labels_widget` for modifying existing work item labels
4. **Verification**: Use `get_work_item` to confirm label assignments

**⚠️ IMPORTANT FOR AI AGENTS**: Always discover existing labels before creating new ones to maintain consistency and prevent label proliferation.

## Breaking Changes from Upstream

This project has been completely refactored from the original repository with significant breaking changes:

### 🔥 **BREAKING CHANGE: Deprecated REST API Removal**
- **Removed**: All deprecated REST API epic and issue tools
- **Replaced**: Modern unified Work Items GraphQL API 
- **Impact**: Any code using `create_epic`, `list_epics`, `get_epic`, `update_epic`, `delete_epic`, `create_issue`, `list_issues`, `get_issue`, `update_issue`, `delete_issue` must migrate to Work Items API
- **Migration**: Use `create_work_item`, `list_work_items`, `get_work_item`, `update_work_item`, `delete_work_item` instead

### 🔥 **BREAKING CHANGE: GraphQL API Requirement**
- **Added Dependency**: `gql` library required for Work Items functionality
- **Configuration**: Must include `gql` in MCP server configuration: `--with mcp[cli],gql`
- **Impact**: Existing installations must update dependencies and configuration

### 🚀 **Current Project Status**

**✅ Production Ready Features:**
- **Work Items API**: Complete GraphQL implementation with comprehensive agentic descriptions
- **Repository Management**: Full CRUD operations for repositories and file management
- **Branch Operations**: Complete branch lifecycle management
- **Merge Requests**: Full merge request workflow support
- **Search Functionality**: Enhanced search with contextual fields across all content types
- **Milestone Management**: Complete milestone lifecycle with UX-optimized schemas
- **Label Management**: Integrated label operations via Work Items API with agent-optimized workflows
- **Iteration Support**: Premium/Ultimate tier iteration management

**✅ Verified & Tested:**
- **Comprehensive Test Suite**: 186 tests covering all functionality with 100% pass rate
- **Integration Testing**: Full end-to-end testing against live GitLab API
- **Unit Testing**: Isolated component testing with mock validation
- **Performance Testing**: Bulk operation and timeout optimization
- **Error Handling**: Comprehensive edge case and exception testing
- **GraphQL Compatibility**: Confirmed with GitLab 18.3+ including dynamic type discovery
- **Field Validation**: Pydantic schema validation for all API responses
- **Test Infrastructure**: Automated cleanup, fixtures, and validation utilities

**🧪 Testing Infrastructure:**
- **186 tests total** with comprehensive coverage of all GitLab operations
- **Integration tests** against live GitLab instance with safety guards
- **Unit tests** for isolated component validation
- **Performance benchmarks** for bulk operations and API efficiency
- **Automated cleanup** preventing test data pollution
- **Dynamic type discovery** for GitLab Work Item types
- **Comprehensive validation** using custom ResponseValidator utilities

**🏗️ Architecture:**
- **Domain-driven structure**: Modular organization by GitLab entities
- **Dual API support**: REST and GraphQL for comprehensive coverage
- **Type safety**: Full Pydantic validation with Python 3.13+ support
- **Enhanced UX**: Optimized field ordering for Claude Code compatibility
- **Comprehensive error handling**: Meaningful error messages and proper exception management
- **Test-driven development**: All features backed by comprehensive test coverage


## Troubleshooting

### Common Issues

- **GitLab API Authentication Errors**: Ensure your `GITLAB_PERSONAL_ACCESS_TOKEN` has the necessary permissions and is correctly set in your environment variables.
- **NoneType errors**: Some functions may encounter issues when handling empty results. If you encounter these errors, please report them with detailed steps to reproduce.

## Authors

- **Adit pal Singh** - Original author
- **Dmitry Prudnikov** - Work Items API implementation, GraphQL migration, and comprehensive enhancements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
