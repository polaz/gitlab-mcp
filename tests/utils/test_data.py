"""Test data generators for GitLab MCP Server tests.

This module provides utilities for generating realistic test data
for GitLab entities like work items, milestones, iterations, etc.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from faker import Faker


class TestDataFactory:
    """Factory for generating test data for GitLab entities."""

    def __init__(self, group_path: str, project_path: str, prefix: str = "TEST_"):
        self.fake = Faker()
        self.group_path = group_path
        self.project_path = project_path
        self.prefix = prefix

        # Seed for reproducible data
        Faker.seed(12345)

        # Common test data pools
        self.common_labels = ["bug", "feature", "enhancement", "documentation", "testing"]
        self.priorities = ["low", "medium", "high", "critical"]
        self.work_item_types = ["EPIC", "ISSUE", "TASK", "INCIDENT", "TEST_CASE", "REQUIREMENT"]

    def generate_uuid(self) -> str:
        """Generate a short UUID for test data."""
        return uuid.uuid4().hex[:8]

    def generate_title(self, entity_type: str = "item") -> str:
        """Generate a test title with prefix."""
        base_title = self.fake.catch_phrase()
        return f"{self.prefix}{entity_type.upper()} {base_title}"

    def generate_description(self, entity_type: str = "item") -> str:
        """Generate a test description in Markdown format."""
        return f"""# {entity_type.title()} Description

{self.fake.paragraph(nb_sentences=3)}

## Details
- Created by: GitLab MCP Test Suite
- Purpose: Testing {entity_type} functionality
- Timestamp: {datetime.now().isoformat()}

## Tasks
{chr(10).join([f"- [ ] {self.fake.sentence()}" for _ in range(3)])}

---
*This is test data generated for GitLab MCP Server testing.*
"""

    def work_item_data(
        self,
        work_item_type: str = "ISSUE",
        title: str | None = None,
        description: str | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """Generate work item creation data."""
        data = {
            "title": title or self.generate_title(work_item_type.lower()),
            "description": description or self.generate_description(work_item_type.lower()),
            "confidential": self.fake.boolean(chance_of_getting_true=20),
        }

        # Add scope based on work item type
        if work_item_type in ["EPIC", "OBJECTIVE", "KEY_RESULT"]:
            data["namespace_path"] = self.group_path
        else:
            data["project_path"] = self.project_path

        # Add any additional kwargs
        data.update(kwargs)

        return data

    def epic_data(self, **kwargs) -> dict[str, Any]:
        """Generate epic creation data."""
        return self.work_item_data(
            work_item_type="EPIC",
            **kwargs
        )

    def issue_data(self, **kwargs) -> dict[str, Any]:
        """Generate issue creation data."""
        return self.work_item_data(
            work_item_type="ISSUE",
            **kwargs
        )

    def task_data(self, parent_id: str | None = None, **kwargs) -> dict[str, Any]:
        """Generate task creation data."""
        data = self.work_item_data(
            work_item_type="TASK",
            **kwargs
        )
        if parent_id:
            data["parent_id"] = parent_id
        return data

    def milestone_data(
        self,
        title: str | None = None,
        is_group_milestone: bool = False,
        **kwargs
    ) -> dict[str, Any]:
        """Generate milestone creation data."""
        start_date = self.fake.date_between(start_date="today", end_date="+30d")
        due_date = start_date + timedelta(days=self.fake.random_int(min=7, max=90))

        data = {
            "title": title or self.generate_title("milestone"),
            "description": self.generate_description("milestone"),
            "start_date": start_date.isoformat(),
            "due_date": due_date.isoformat(),
        }

        # Add scope
        if is_group_milestone:
            data["group_id"] = self.group_path
        else:
            data["project_path"] = self.project_path

        data.update(kwargs)
        return data

    def iteration_data(
        self,
        title: str | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """Generate iteration creation data."""
        start_date = self.fake.date_between(start_date="today", end_date="+30d")
        due_date = start_date + timedelta(days=14)  # 2-week sprint

        data = {
            "group_id": self.group_path,
            "title": title or self.generate_title("iteration"),
            "description": self.generate_description("iteration"),
            "start_date": start_date.isoformat(),
            "due_date": due_date.isoformat(),
        }

        data.update(kwargs)
        return data

    def branch_data(
        self,
        branch_name: str | None = None,
        ref: str = "main",
        **kwargs
    ) -> dict[str, Any]:
        """Generate branch creation data."""
        data = {
            "project_path": self.project_path,
            "branch_name": branch_name or f"{self.prefix.lower()}branch-{self.generate_uuid()}",
            "ref": ref,
        }

        data.update(kwargs)
        return data

    def label_data(self, **kwargs) -> dict[str, Any]:
        """Generate label creation data."""
        data = {
            "name": f"{self.prefix}label-{self.generate_uuid()}",
            "color": self.fake.hex_color(),
            "description": "Test label created by GitLab MCP Test Suite",
        }

        data.update(kwargs)
        return data

    def search_terms(self) -> list[str]:
        """Generate realistic search terms for testing."""
        return [
            self.prefix.rstrip("_"),  # Search for test prefix
            "bug",
            "feature",
            "documentation",
            self.fake.word(),
            f"author:{self.fake.user_name()}",
            "state:opened",
            "label:bug",
        ]

    def bulk_work_items_data(
        self,
        count: int = 5,
        work_item_type: str = "ISSUE"
    ) -> list[dict[str, Any]]:
        """Generate multiple work items data for bulk testing."""
        return [
            self.work_item_data(
                work_item_type=work_item_type,
                title=f"{self.generate_title(work_item_type.lower())} #{i+1}"
            )
            for i in range(count)
        ]

    def hierarchy_data(self) -> dict[str, Any]:
        """Generate data for testing work item hierarchy."""
        epic_data = self.epic_data(title=f"{self.prefix}Epic - Main Feature")

        issues_data = [
            self.issue_data(title=f"{self.prefix}Issue - Authentication"),
            self.issue_data(title=f"{self.prefix}Issue - Authorization"),
            self.issue_data(title=f"{self.prefix}Issue - User Management"),
        ]

        # Tasks will be created with parent_id after issues are created
        tasks_templates = [
            {"title": f"{self.prefix}Task - Login Form"},
            {"title": f"{self.prefix}Task - Password Reset"},
            {"title": f"{self.prefix}Task - User Registration"},
        ]

        return {
            "epic": epic_data,
            "issues": issues_data,
            "tasks_templates": tasks_templates,
        }

    def edge_case_data(self) -> dict[str, Any]:
        """Generate edge case test data."""
        return {
            "empty_title": {
                "title": "",  # Invalid: empty title
                "description": self.generate_description("invalid"),
                "project_path": self.project_path,
            },
            "long_title": {
                "title": "A" * 300,  # Invalid: too long title
                "description": self.generate_description("invalid"),
                "project_path": self.project_path,
            },
            "special_chars_title": {
                "title": f"{self.prefix}Title with 特殊字符 émojis 🚀 and symbols!@#$%",
                "description": self.generate_description("special"),
                "project_path": self.project_path,
            },
            "markdown_injection": {
                "title": f"{self.prefix}Title with [markdown](http://example.com)",
                "description": """# Markdown Test
```javascript
console.log('code injection test');
```
[Link test](http://example.com)
![Image test](http://example.com/image.png)
""",
                "project_path": self.project_path,
            },
            "unicode_content": {
                "title": f"{self.prefix}Unicode: 日本語 العربية Русский 中文",
                "description": """# Unicode Test
This content contains various Unicode characters:
- Japanese: こんにちは世界
- Arabic: مرحبا بالعالم
- Russian: Привет мир
- Chinese: 你好世界
- Emoji: 🌍🚀💻🔥⭐
""",
                "project_path": self.project_path,
            }
        }

    def performance_test_data(self, count: int = 100) -> list[dict[str, Any]]:
        """Generate large amounts of test data for performance testing."""
        return [
            {
                "title": f"{self.prefix}Performance Test Item {i+1:04d}",
                "description": f"Performance test work item #{i+1}\\n\\nGenerated at {datetime.now().isoformat()}",
                "project_path": self.project_path,
            }
            for i in range(count)
        ]

    def date_range_data(self) -> dict[str, dict[str, Any]]:
        """Generate test data with various date scenarios."""
        now = datetime.now()

        return {
            "past_dates": {
                "start_date": (now - timedelta(days=30)).date().isoformat(),
                "due_date": (now - timedelta(days=15)).date().isoformat(),
            },
            "future_dates": {
                "start_date": (now + timedelta(days=7)).date().isoformat(),
                "due_date": (now + timedelta(days=21)).date().isoformat(),
            },
            "invalid_order": {
                "start_date": (now + timedelta(days=30)).date().isoformat(),
                "due_date": (now + timedelta(days=15)).date().isoformat(),  # Due before start
            },
            "same_dates": {
                "start_date": now.date().isoformat(),
                "due_date": now.date().isoformat(),
            },
        }

    def state_transition_data(self) -> list[dict[str, Any]]:
        """Generate data for testing state transitions."""
        return [
            {"state_event": "close", "expected_state": "CLOSED"},
            {"state_event": "reopen", "expected_state": "OPEN"},
        ]

    def widget_test_data(self) -> dict[str, Any]:
        """Generate data for testing various widgets."""
        return {
            "assignees": {
                "assignee_usernames": ["test-user-1", "test-user-2"],
            },
            "labels": {
                "labels": [f"{self.prefix}label1", f"{self.prefix}label2"],
            },
            "dates": {
                "start_date": datetime.now().date().isoformat(),
                "due_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
            },
            "weight": {
                "weight": self.fake.random_int(min=1, max=10),
            },
        }

    def file_data(self, **kwargs) -> dict[str, Any]:
        """Generate file creation data."""
        data = {
            "name": f"{self.prefix.lower()}file-{self.generate_uuid()}",
            "content": self.generate_description("file"),
            "commit_message": "Create test file via GitLab MCP Test Suite",
            "timestamp": datetime.now().isoformat(),
        }

        data.update(kwargs)
        return data

    def unicode_data(self, **kwargs) -> dict[str, Any]:
        """Generate unicode content data for testing."""
        data = {
            "title": f"{self.prefix}Unicode: 日本語 العربية Русский 中文",
            "description": """# Unicode Test
This content contains various Unicode characters:
- Japanese: こんにちは世界
- Arabic: مرحبا بالعالم
- Russian: Привет мир
- Chinese: 你好世界
- Emoji: 🌍🚀💻🔥⭐
""",
        }

        data.update(kwargs)
        return data

    def large_content_data(self, **kwargs) -> dict[str, Any]:
        """Generate large content data for testing."""
        # Create a large description by repeating paragraphs
        base_paragraph = self.fake.paragraph(nb_sentences=10)
        large_description = "\n\n".join([
            f"Section {i+1}: {base_paragraph}"
            for i in range(100)  # 100 sections of text
        ])

        data = {
            "name": f"{self.prefix.lower()}large-{self.generate_uuid()}",
            "description": large_description,
        }

        data.update(kwargs)
        return data

    def repository_data(self, **kwargs) -> dict[str, Any]:
        """Generate repository/project data.

        Args:
            **kwargs: Override fields in the generated data.

        Returns:
            dict[str, Any]: Dictionary containing repository data.
        """
        data = {
            "name": f"{self.prefix.lower()}repo-{self.generate_uuid()}",
            "description": self.generate_description("repository"),
            "namespace_id": self.group_path,  # Use group path as namespace
            "visibility": "private",
        }

        data.update(kwargs)
        return data
