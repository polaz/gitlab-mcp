# GitLab Work Items API Comprehensive Guide

## Work Item Types and Their Use Cases

### 🎯 **EPIC** (Group-scoped)
**Purpose:** High-level container for organizing related work across multiple projects
**Hierarchy:** Top-level parent for issues, tasks, and child epics  
**Scope:** Group/namespace level (use `namespace_path`)
**Common Use:**
- Feature roadmap planning
- Initiative tracking across teams
- Release planning
- Cross-project coordination

**Parent-Child Relations:**
- **Parents:** Can have parent epics (epic hierarchy)
- **Children:** Issues, Tasks, Child Epics, Incidents, Requirements

---

### 🐛 **ISSUE** (Project-scoped)
**Purpose:** Individual work items, bugs, features within a project
**Hierarchy:** Can be child of epics, parent of tasks
**Scope:** Project level (use `project_path`)
**Common Use:**
- Bug reports
- Feature requests  
- User stories
- Technical debt items

**Parent-Child Relations:**
- **Parents:** Epics, parent issues
- **Children:** Tasks, child issues

---

### ✅ **TASK** (Project-scoped)
**Purpose:** Granular work items, subtasks, actionable items
**Hierarchy:** Child of issues or epics, can have sub-tasks
**Scope:** Project level (use `project_path`)
**Common Use:**
- Breaking down issues into smaller work
- Checklist items
- Implementation steps
- Code review tasks

**Parent-Child Relations:**
- **Parents:** Issues, Epics
- **Children:** Sub-tasks

---

### 🎖️ **OBJECTIVE** (Group-scoped)
**Purpose:** OKR (Objectives and Key Results) framework goals
**Hierarchy:** Parent of key results
**Scope:** Group/namespace level (use `namespace_path`)
**Common Use:**
- Quarterly objectives
- Strategic goals
- Team targets
- Business outcomes

**Parent-Child Relations:**
- **Parents:** None (top-level)
- **Children:** Key Results

---

### 📊 **KEY_RESULT** (Group-scoped)
**Purpose:** Measurable outcomes for objectives (OKR framework)
**Hierarchy:** Child of objectives
**Scope:** Group/namespace level (use `namespace_path`)
**Common Use:**
- Measurable targets
- KPI tracking
- Success metrics
- Progress indicators

**Parent-Child Relations:**
- **Parents:** Objectives
- **Children:** None (leaf level)

---

### 🚨 **INCIDENT** (Project-scoped)
**Purpose:** Urgent issues requiring immediate attention
**Hierarchy:** Can be child of epics, parent of tasks
**Scope:** Project level (use `project_path`)
**Common Use:**
- Service outages
- Security incidents
- Critical bugs
- Emergency fixes

**Parent-Child Relations:**
- **Parents:** Epics
- **Children:** Tasks, resolution steps

---

### 🧪 **TEST_CASE** (Project-scoped)
**Purpose:** Test scenarios and quality assurance items
**Hierarchy:** Can be child of requirements or issues
**Scope:** Project level (use `project_path`)
**Common Use:**
- Manual test cases
- Automated test planning
- QA scenarios
- Acceptance criteria

**Parent-Child Relations:**
- **Parents:** Requirements, Issues
- **Children:** Test steps (as tasks)

---

### 📋 **REQUIREMENT** (Project-scoped)
**Purpose:** Formal requirements and specifications
**Hierarchy:** Can be child of epics, parent of test cases
**Scope:** Project level (use `project_path`)
**Common Use:**
- Functional requirements
- Technical specifications
- Compliance requirements
- Documentation needs

**Parent-Child Relations:**
- **Parents:** Epics
- **Children:** Test Cases, Implementation Issues

---

## Widget Architecture

### 🏗️ **HIERARCHY Widget**
**Purpose:** Parent/child relationships between work items
**Operations:** Add/remove parent, add/remove children, reorder
**Key Fields:** `parent`, `children`

### 👥 **ASSIGNEES Widget**
**Purpose:** User assignment and ownership
**Operations:** Assign/unassign users
**Key Fields:** `assignees` array

### 🏷️ **LABELS Widget**
**Purpose:** Categorization and tagging
**Operations:** Add/remove labels
**Key Fields:** `labels` array

### 🎯 **MILESTONE Widget**
**Purpose:** Release and deadline tracking
**Operations:** Set/clear milestone
**Key Fields:** `milestone`

### 🔄 **ITERATION Widget**
**Purpose:** Sprint/iteration assignment (Agile)
**Operations:** Set/clear iteration
**Key Fields:** `iteration`

### 📅 **START_AND_DUE_DATE Widget**
**Purpose:** Time planning and scheduling
**Operations:** Set/clear dates
**Key Fields:** `start_date`, `due_date`

### 📝 **DESCRIPTION Widget**
**Purpose:** Detailed content and documentation
**Operations:** Update description
**Key Fields:** `description` (Markdown)

### 💬 **NOTES Widget**
**Purpose:** Comments and discussions
**Operations:** Add/view comments
**Key Fields:** Comments are typically fetched separately

### 📊 **PROGRESS Widget**
**Purpose:** Completion tracking (for objectives/key results)
**Operations:** Update progress percentage
**Key Fields:** `progress` (0-100)

### 🏥 **HEALTH_STATUS Widget** (Ultimate tier)
**Purpose:** Status indication for complex work
**Operations:** Set health status
**Values:** `ON_TRACK`, `NEEDS_ATTENTION`, `AT_RISK`

### ⚖️ **WEIGHT Widget**
**Purpose:** Effort estimation and planning
**Operations:** Set/clear weight
**Key Fields:** `weight` (integer)

---

## Common Hierarchy Patterns

### Epic-driven Development:
```
EPIC (namespace-scoped)
├── ISSUE (project A)
│   ├── TASK (subtask 1)
│   └── TASK (subtask 2)
├── ISSUE (project B)
└── REQUIREMENT (project C)
    └── TEST_CASE (validation)
```

### OKR Structure:
```
OBJECTIVE (namespace-scoped)
├── KEY_RESULT (metric 1)
├── KEY_RESULT (metric 2)
└── KEY_RESULT (metric 3)
```

### Incident Response:
```
INCIDENT (project-scoped)
├── TASK (investigate)
├── TASK (fix implementation)
└── TASK (post-mortem)
```

---

## Scope Guidelines

### Use `namespace_path` for:
- EPIC (group-level coordination)
- OBJECTIVE (organization goals)
- KEY_RESULT (OKR metrics)

### Use `project_path` for:
- ISSUE (project-specific work)
- TASK (implementation details)
- INCIDENT (service-specific problems)
- TEST_CASE (project QA)
- REQUIREMENT (project specs)

---

## Work Item Type IDs

Work item type IDs are unique identifiers required for creation:
- Each GitLab instance has its own type IDs
- Types can be custom-configured per organization
- Use the GraphQL schema to discover available types
- Standard types are usually available but IDs vary

Common pattern: `gid://gitlab/WorkItems::Type/{id}`

---

## Common and Specific Fields by Work Item Type

### 🔗 **COMMON FIELDS (All Work Item Types)**

#### Core Identity:
- `iid`: Internal ID (unique within project/namespace)
- `id`: Global GraphQL ID (e.g., "gid://gitlab/WorkItem/123")
- `title`: Display name of the work item
- `state`: OPEN (active) or CLOSED (completed)
- `work_item_type`: Type information {id, name, icon_name}

#### Timestamps:
- `created_at`: Creation timestamp (ISO 8601)
- `updated_at`: Last modification timestamp
- `closed_at`: Closure timestamp (null if open)

#### Context:
- `author`: Creator details {id, name, username, avatar_url}
- `web_url`: Direct link to view in GitLab UI
- `reference`: Short reference format (e.g., "#123", "&42")
- `confidential`: Privacy flag (boolean)

#### Navigation:
- `project`: Project context (for project-scoped items)
- `namespace`: Group/namespace context (for group-scoped items)

---

### 🎯 **EPIC-SPECIFIC FIELDS**

#### Scope & Organization:
- `namespace`: Group information {id, name, full_path, visibility}
- `group`: Alias for namespace
- `color`: Epic color theme {id, color}
- `parent`: Parent epic (for epic hierarchies)
- `descendant_counts`: Child statistics {opened_epics, closed_epics, opened_issues, closed_issues}

#### Epic Widgets:
- `HIERARCHY`: Complex parent/child relationships across projects
- `LABELS`: Group-level labels for epic categorization
- `DATES`: Strategic planning dates (start_date, due_date)
- `DESCRIPTION`: Rich markdown content with epic overview
- `HEALTH_STATUS`: Epic health indicator (Ultimate tier)

---

### 🐛 **ISSUE-SPECIFIC FIELDS**

#### Project Context:
- `project`: Project details {id, name, path, visibility}
- `issue_type`: Classification {id, name, description} - bug, feature, task
- `service_desk_reply_to`: Service desk email (if applicable)

#### Issue Metadata:
- `time_estimate`: Estimated work time (seconds)
- `time_spent`: Actual work time logged (seconds)
- `human_time_estimate`: Human-readable estimate ("2h 30m")
- `human_total_time_spent`: Human-readable spent time
- `merge_requests_count`: Related MR count

#### Issue Widgets:
- `ASSIGNEES`: User assignments with roles
- `LABELS`: Project and group labels
- `MILESTONE`: Release planning
- `ITERATION`: Sprint assignment
- `WEIGHT`: Story points/effort estimation
- `DUE_DATE`: Deadline tracking
- `TIME_TRACKING`: Time logging and estimates

---

### ✅ **TASK-SPECIFIC FIELDS**

#### Task Context:
- `project`: Parent project information
- `parent_issue`: Parent issue reference (if applicable)
- `task_completion_status`: Subtask progress tracking

#### Task Widgets:
- `HIERARCHY`: Strong parent-child relationships (usually under issues)
- `ASSIGNEES`: Task ownership (often single assignee)
- `LABELS`: Task categorization
- `START_AND_DUE_DATE`: Task scheduling
- `DESCRIPTION`: Implementation details
- `WEIGHT`: Task complexity estimation

---

### 🎖️ **OBJECTIVE-SPECIFIC FIELDS**

#### Strategic Context:
- `namespace`: Organization/team scope
- `objective_level`: Strategic level (organization, team, individual)
- `time_period`: Planning period {start_date, end_date}

#### OKR Widgets:
- `PROGRESS`: Overall objective progress (calculated from key results)
- `HIERARCHY`: Key results as children
- `HEALTH_STATUS`: Strategic health indicator
- `DATES`: Planning and review cycles
- `DESCRIPTION`: Strategic context and success criteria

---

### 📊 **KEY_RESULT-SPECIFIC FIELDS**

#### Measurement:
- `target_value`: Target metric value
- `current_value`: Current progress value
- `unit`: Measurement unit (percentage, count, currency)
- `progress`: Calculated progress percentage (0-100)

#### Key Result Widgets:
- `PROGRESS`: Primary widget for metric tracking
- `HIERARCHY`: Parent objective relationship
- `ASSIGNEES`: KR owners and contributors
- `DATES`: Measurement periods
- `DESCRIPTION`: Measurement methodology

---

### 🚨 **INCIDENT-SPECIFIC FIELDS**

#### Incident Management:
- `severity`: Incident severity level {id, name, description}
- `priority`: Response priority (Critical, High, Medium, Low)
- `escalation_status`: Escalation state and timeline
- `resolution_summary`: Resolution details and root cause

#### Incident Widgets:
- `ASSIGNEES`: Incident response team
- `LABELS`: Incident categorization (outage, security, performance)
- `START_AND_DUE_DATE`: Incident timeline and SLA
- `HEALTH_STATUS`: Incident status progression
- `HIERARCHY`: Response tasks and follow-up actions

---

### 🧪 **TEST_CASE-SPECIFIC FIELDS**

#### Test Management:
- `test_status`: Execution status {id, name} - passed, failed, skipped
- `automation_status`: Automation level (manual, automated, semi-automated)
- `test_suite`: Test suite grouping
- `execution_time`: Test execution duration

#### Test Case Widgets:
- `HIERARCHY`: Test requirements and parent test suites
- `LABELS`: Test categorization (smoke, regression, integration)
- `ASSIGNEES`: Test owners and executors
- `DESCRIPTION`: Test steps and expected results
- `NOTES`: Test execution notes and results

---

### 📋 **REQUIREMENT-SPECIFIC FIELDS**

#### Requirement Management:
- `requirement_type`: Classification {id, name} - functional, non-functional, compliance
- `compliance_framework`: Regulatory framework reference
- `acceptance_criteria`: Structured acceptance conditions
- `verification_status`: Verification state and evidence

#### Requirement Widgets:
- `HIERARCHY`: Parent epics and child test cases
- `LABELS`: Requirement categorization
- `ASSIGNEES`: Requirement owners and reviewers
- `DESCRIPTION`: Detailed requirement specification
- `NOTES`: Review comments and clarifications

---

## Widget Field Details

### 👥 **ASSIGNEES Widget Structure**
```json
{
  "type": "ASSIGNEES",
  "assignees": [
    {
      "id": "gid://gitlab/User/123",
      "name": "John Doe",
      "username": "john.doe",
      "avatar_url": "https://...",
      "web_url": "https://gitlab.com/john.doe",
      "state": "active"
    }
  ]
}
```

### 🏷️ **LABELS Widget Structure**
```json
{
  "type": "LABELS",
  "labels": [
    {
      "id": "gid://gitlab/Label/456",
      "title": "bug",
      "color": "#d9534f",
      "description": "Something isn't working",
      "text_color": "#FFFFFF"
    }
  ]
}
```

### 🏗️ **HIERARCHY Widget Structure**
```json
{
  "type": "HIERARCHY",
  "parent": {
    "id": "gid://gitlab/WorkItem/789",
    "iid": 42,
    "title": "Parent Epic",
    "work_item_type": {"name": "Epic"}
  },
  "children": [
    {
      "id": "gid://gitlab/WorkItem/790",
      "iid": 15,
      "title": "Child Task",
      "work_item_type": {"name": "Task"}
    }
  ]
}
```

### 🎯 **MILESTONE Widget Structure**
```json
{
  "type": "MILESTONE",
  "milestone": {
    "id": "gid://gitlab/Milestone/101",
    "title": "v2.0 Release",
    "description": "Major feature release",
    "state": "active",
    "due_date": "2024-03-31",
    "start_date": "2024-01-01",
    "web_url": "https://..."
  }
}
```

### 🔄 **ITERATION Widget Structure**
```json
{
  "type": "ITERATION",
  "iteration": {
    "id": "gid://gitlab/Iteration/202",
    "title": "Sprint 15",
    "description": "Q1 Sprint 15",
    "state": "opened",
    "start_date": "2024-01-15",
    "due_date": "2024-01-29",
    "web_url": "https://..."
  }
}
```

### 📅 **DATES Widget Structure**
```json
{
  "type": "START_AND_DUE_DATE",
  "start_date": "2024-01-01",
  "due_date": "2024-01-31"
}
```

### 📊 **PROGRESS Widget Structure**
```json
{
  "type": "PROGRESS",
  "progress": 75,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 🏥 **HEALTH_STATUS Widget Structure**
```json
{
  "type": "HEALTH_STATUS", 
  "health_status": "ON_TRACK",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### ⚖️ **WEIGHT Widget Structure**  
```json
{
  "type": "WEIGHT",
  "weight": 5
}
```