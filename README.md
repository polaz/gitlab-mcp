# GitLab MCP Server

A MCP (Model Context Protocol) server for interacting with GitLab API. This server provides a set of tools that allow AI clients to perform operations on GitLab repositories, issues, merge requests, and more. All operations support both synchronous and asynchronous execution patterns.

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://gitlab.devops.telekom.de/adit-pal.singh/gitlab-mcp.git
cd gitlab-mcp

# Install dependencies using uv
uv sync
```

### Using pip

```bash
# Clone the repository
git clone https://gitlab.devops.telekom.de/adit-pal.singh/gitlab-mcp.git
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
GITLAB_API_URL=https://gitlab.devops.telekom.de
```

### Option 2: MCP Configuration

You can also configure the MCP server in your MCP JSON configuration file:

```json
{
  "mcpServers": {
    "gitlab-mcp": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli],python-gitlab", "mcp", "run", "/path/to/gitlab-mcp/server.py"],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "your_personal_access_token",
        "GITLAB_API_URL": "https://gitlab.devops.telekom.de"
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
│   │   └── users.py               # User data models
│   ├── services/                  # Business logic layer
│   │   ├── repositories.py        # Repository operations
│   │   ├── branches.py            # Branch operations
│   │   ├── issues.py              # Issue operations
│   │   ├── merge_requests.py      # Merge request operations
│   │   ├── pipelines.py           # Pipeline operations
│   │   ├── groups.py              # Group operations
│   │   └── users.py               # User operations
│   └── tools/                     # MCP tool implementations
│       ├── repositories.py        # Repository tools
│       ├── branches.py            # Branch tools
│       ├── issues.py              # Issue tools
│       ├── merge_requests.py      # Merge request tools
│       ├── pipelines.py           # Pipeline tools
│       ├── groups.py              # Group tools
│       └── users.py               # User tools
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

- `fork_repository`: Fork a GitLab repository
- `create_repository`: Create a new GitLab repository
- `search_projects`: Search for GitLab projects by name or keyword

### Branch Operations

- `create_branch`: Create a new branch in a GitLab repository
- `get_default_branch_ref`: Get the default branch reference for a GitLab repository

### File Operations

- `get_file_contents`: Retrieve the contents of a file from a GitLab repository

### Issue Management

- `create_issue`: Create a new issue in a GitLab repository
- `list_issues`: List issues for a GitLab project
- `get_issue`: Get details for a specific GitLab issue
- `comment_on_issue`: Add a comment to a GitLab issue
- `list_issue_comments`: List comments for a GitLab issue
- `close_issue`: Close a GitLab issue

### Merge Request Operations

- `create_merge_request`: Create a new merge request in a GitLab repository
- `list_merge_requests`: List merge requests for a GitLab project
- `get_merge_request`: Get details for a specific GitLab merge request
- `comment_on_merge_request`: Add a comment to a GitLab merge request
- `list_merge_request_comments`: List comments for a GitLab merge request
- `list_merge_request_changes`: List files changed in a GitLab merge request
- `get_merge_request_diff`: Get the diff for a specific file in a GitLab merge request
- `suggest_code_in_merge_request`: Create a code suggestion comment on a GitLab merge request
- `approve_merge_request`: Approve a GitLab merge request
- `merge_merge_request`: Merge a GitLab merge request
- `close_merge_request`: Close a GitLab merge request

### Pipeline Management (New)

- `list_pipelines`: List pipelines in a GitLab project
- `get_pipeline`: Get a specific pipeline from a GitLab project
- `create_pipeline`: Create a new pipeline in a GitLab project
- `pipeline_action`: Perform an action on a GitLab pipeline (cancel or retry)

### Group Operations (New - Read-only)

- `list_groups`: List GitLab groups
- `get_group`: Get a specific GitLab group

### User Operations (New - Read-only)

- `list_users`: List GitLab users
- `get_user`: Get a specific GitLab user

## Troubleshooting

### Common Issues

- **GitLab API Authentication Errors**: Ensure your `GITLAB_PERSONAL_ACCESS_TOKEN` has the necessary permissions and is correctly set in your environment variables.
- **NoneType errors**: Some functions may encounter issues when handling empty results. If you encounter these errors, please report them with detailed steps to reproduce.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Merge Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
