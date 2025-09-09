# GitLab MCP Server

A MCP (Model Context Protocol) server for interacting with GitLab API. This server provides a set of tools that allow AI clients to perform operations on GitLab repositories, issues, merge requests, and more. All operations support both synchronous and asynchronous execution patterns.

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/Adit-999/gitlab-mcp.git
cd gitlab-mcp

# Install dependencies using uv
uv sync
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/Adit-999/gitlab-mcp.git
cd gitlab-mcp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

The GitLab MCP server requires two environment variables to function properly:

1. `GITLAB_PERSONAL_ACCESS_TOKEN` - For authentication with GitLab API
2. `GITLAB_API_URL` - The base URL for the GitLab API

### Option 1: Environment Variables

Create a `.env` file in the project root directory with these variables:

```
GITLAB_PERSONAL_ACCESS_TOKEN=your_personal_access_token
GITLAB_API_URL=https://gitlab.com
```

### Option 2: MCP Configuration

You can also configure the MCP server in your MCP JSON configuration file:

```json
{
  "mcpServers": {
    "gitlab-mcp": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "mcp", "run", "/path/to/gitlab-mcp/server.py"],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "your_personal_access_token",
        "GITLAB_API_URL": "https://gitlab.com"
      }
    }
  }
}
```

### Configure with uv for Claude Desktop

```bash
uv run mcp install server.py
```
## Project Structure

The project follows a modular, domain-driven architecture:

```
gitlab-mcp/
├── src/                           # Source code
│   ├── api/                       # API interaction layer
│   │   ├── rest_client.py         # GitLab REST API client
│   │   ├── exceptions.py          # API exception definitions
│   ├── schemas/                   # Data models and validation
│   │   ├── base.py                # Base schema classes
│   │   ├── repositories.py        # Repository data models
│   │   ├── branches.py            # Branch data models
│   │   ├── issues.py              # Issue data models
│   │   ├── merge_requests.py      # Merge request data models
│   │   ├── groups.py              # Group data models
│   │   ├── labels.py              # Label data models
│   │   └── search.py              # Search data models
│   ├── services/                  # Business logic layer
│   │   ├── repositories.py        # Repository operations
│   │   ├── branches.py            # Branch operations
│   │   ├── issues.py              # Issue operations
│   │   ├── merge_requests.py      # Merge request operations
│   │   ├── groups.py              # Group operations
│   │   ├── labels.py              # Label operations
│   │   └── search.py              # Search operations
│   └── tools/                     # MCP tool implementations
│       ├── repositories.py        # Repository tools
│       ├── branches.py            # Branch tools
│       ├── issues.py              # Issue tools
│       ├── merge_requests.py      # Merge request tools
│       ├── groups.py              # Group tools
│       ├── labels.py              # Label tools
│       └── search.py              # Search tools
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

### Issue Management

- `create_issue`: Create a new issue in a GitLab repository
- `list_all_issues`: List issues globally or from a specific project with optional label filtering
- `get_issue`: Get details for a specific GitLab issue
- `update_issue`: Update an existing issue with comprehensive field support including assignees, labels, state, milestones, and metadata
- `close_issue`: Close a GitLab issue
- `delete_issue`: Delete an issue from a GitLab repository
- `move_issue`: Move an issue to a different project
- `comment_on_issue`: Add a comment to a GitLab issue
- `list_issue_comments`: List comments for a GitLab issue

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

- `search_globally`: Search for projects, file contents (blobs), and wiki content across all accessible GitLab instances. Does NOT search issues or merge requests.
- `search_project`: Search for file contents (blobs), wiki content, and project metadata within a specific project. Does NOT search issues or merge requests.
- `search_group`: Search for projects, file contents (blobs), and wiki content within a specific group. Does NOT search issues or merge requests.

### Label Operations

- `list_labels`: List GitLab labels at project or group level
- `get_label`: Get details for a specific GitLab label
- `create_label`: Create a new GitLab label
- `update_label`: Update an existing GitLab label
- `delete_label`: Delete a GitLab label
- `subscribe_to_label`: Subscribe to a GitLab project label
- `unsubscribe_from_label`: Unsubscribe from a GitLab project label

## Project Enhancements

This fork includes several improvements and fixes beyond the original repository:

### Label Management System
- **Complete label CRUD operations**: Full support for creating, reading, updating, and deleting labels at both project and group levels
- **Label subscriptions**: Subscribe/unsubscribe functionality for project labels
- **Enhanced issue filtering**: Added label filtering capability to `list_all_issues` for improved issue organization

### Issues API Enhancement  
- **Flexible issue querying**: Enhanced `list_all_issues` to support both global (`/issues`) and project-specific (`/projects/{id}/issues`) endpoints
- **Optional project scoping**: Made project_path parameter optional to enable cross-project issue searches
- **Label-based filtering**: Verified label filtering works correctly with project-specific queries (e.g., area::ux labels)
- **Comprehensive issue updates**: Added `update_issue` function with full GitLab API support for assignees, labels, milestones, epic linking, and metadata

### API Compatibility & Error Handling
- **GitLab API 18.3/18.4 compatibility**: Updated schemas and API calls to work with latest GitLab versions
- **Improved error handling**: Fixed recursive error wrapping in group operations that was creating confusing nested error messages
- **Parameter validation**: Enhanced parameter handling to prevent invalid API calls (e.g., null state values)

### Schema & Type Safety
- **Modern Python 3.13 support**: Updated generic type syntax from `Generic[T]` to modern `[T]` syntax
- **Flexible data models**: Made optional fields truly optional in GitLabLabel schema to handle API response variations
- **Better validation**: Improved Pydantic schema validation for edge cases

### Code Quality & Architecture
- **Fixed parameter naming**: Corrected `data` vs `json_data` parameter mismatches in REST client calls
- **Environment loading**: Added proper .env file loading for configuration management
- **Comprehensive testing**: All label functions verified against live GitLab API
- **Python version flexibility**: Supports both Python 3.12 and 3.13 with proper virtual environment management
- **Clarified tool limitations**: Enhanced search tool descriptions to prevent misuse (e.g., searching for issues when tools only support projects/blobs)

### Bug Fixes
- Fixed syntax errors in base schema classes
- Resolved POST/PUT request parameter naming inconsistencies
- Corrected subscribe/unsubscribe functions missing required parameters
- Fixed group label fetching errors due to schema mismatches

## Troubleshooting

### Common Issues

- **GitLab API Authentication Errors**: Ensure your `GITLAB_PERSONAL_ACCESS_TOKEN` has the necessary permissions and is correctly set in your environment variables.
- **NoneType errors**: Some functions may encounter issues when handling empty results. If you encounter these errors, please report them with detailed steps to reproduce.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
