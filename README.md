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
│   │   ├── client.py              # GitLab client wrapper
│   │   ├── exceptions.py          # API exception definitions
│   │   └── async_utils.py         # Async support utilities
│   ├── schemas/                   # Data models and validation
│   │   ├── base.py                # Base schema classes
│   │   ├── repositories.py        # Repository data models
│   │   ├── branches.py            # Branch data models
│   │   ├── issues.py              # Issue data models
│   │   ├── merge_requests.py      # Merge request data models
│   │   ├── pipelines.py           # Pipeline data models
│   │   ├── groups.py              # Group data models
│   │   └── search.py              # search data models
│   ├── services/                  # Business logic layer
│   │   ├── repositories.py        # Repository operations
│   │   ├── branches.py            # Branch operations
│   │   ├── issues.py              # Issue operations
│   │   ├── merge_requests.py      # Merge request operations
│   │   ├── pipelines.py           # Pipeline operations
│   │   ├── groups.py              # Group operations
│   │   └── search.py              # search operations
│   └── tools/                     # MCP tool implementations
│       ├── repositories.py        # Repository tools
│       ├── branches.py            # Branch tools
│       ├── issues.py              # Issue tools
│       ├── merge_requests.py      # Merge request tools
│       ├── pipelines.py           # Pipeline tools
│       ├── groups.py              # Group tools
│       └── search.py              # search tools
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
- `get_raw_file_contents`: Retrieve the raw contents of a file from a GitLab repository
- `update_file`: Update an existing file in a GitLab repository
- `delete_file`: Delete a file from a GitLab repository
- `get_file_blame`: Retrieve blame information for a file in a GitLab repository

### Issue Management

- `create_issue`: Create a new issue in a GitLab repository
- `update_issue`: Update an existing issue in a GitLab repository
- `list_issues`: List issues for a GitLab project
- `list_all_issues`: List all issues the authenticated user has access to
- `list_group_issues`: List issues in a GitLab group
- `get_issue`: Get details for a specific GitLab issue
- `close_issue`: Close a GitLab issue
- `delete_issue`: Delete an issue from a GitLab repository
- `move_issue`: Move an issue to a different project
- `comment_on_issue`: Add a comment to a GitLab issue
- `list_issue_comments`: List comments for a GitLab issue
- `create_issue_link`: Create a link between issues
- `list_issue_links`: List links to an issue
- `get_issue_link`: Get details about an issue link
- `delete_issue_link`: Delete a link between issues

### Merge Request Operations

- `create_merge_request`: Create a new merge request in a GitLab repository
- `list_merge_requests`: List merge requests for a GitLab project
- `get_merge_request`: Get details for a specific GitLab merge request
- `merge_merge_request`: Merge a GitLab merge request

### Pipeline Management

- `list_project_pipelines`: List pipelines in a GitLab project
- `get_single_pipeline`: Get a single pipeline by ID for a GitLab project
- `get_latest_pipeline`: Get the latest pipeline for the most recent commit on a specific ref

### Job Operations

- `get_job`: Get a specific job from a GitLab project
- `get_job_logs`: Get logs from a GitLab job
- `get_job_failure_info`: Get detailed information about why a GitLab job failed, including error messages from logs

### Group Operations

- `list_groups`: List GitLab groups
- `get_group`: Get a specific GitLab group
- `get_group_by_project_namespace`: Get a GitLab group based on a project namespace

### Search Tools

- `search_global`: Search across all GitLab resources (projects, issues, merge requests, milestones, users, etc.)
- `search_project`: Search within a specific project (issues, merge requests, code content, wiki content, etc.)
- `search_group`: Search within a specific group (projects, issues, merge requests, milestones, etc.)

## Troubleshooting

### Common Issues

- **GitLab API Authentication Errors**: Ensure your `GITLAB_PERSONAL_ACCESS_TOKEN` has the necessary permissions and is correctly set in your environment variables.
- **NoneType errors**: Some functions may encounter issues when handling empty results. If you encounter these errors, please report them with detailed steps to reproduce.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
