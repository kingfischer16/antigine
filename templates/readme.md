# Templates
Template files for use in management of the game design project and its associated artifacts.

## **`template_project.json`**
Template configuration file used when creating new projects. Contains project metadata including:
- Project name and initials (used for feature ID generation)
- Project description and version
- Target programming language and game engine/framework
- Documentation and repository URLs

This file is copied to `.antigine/project.json` during project setup and can be customized by users.

## **SQLite Ledger Database Schema**
The project ledger uses a SQLite database (`ledger.db`) stored in the `.antigine` folder. The database contains three main tables:

### **`features` Table**
Primary table storing feature metadata:

| Column | Type | Description |
| ------ | ---- | ----------- |
| `feature_id` | TEXT PRIMARY KEY | Unique identifier (e.g., "MP-001") composed of project initials + sequential number |
| `type` | TEXT | Feature type: 'new_feature', 'bug_fix', 'refactor', 'enhancement' |
| `status` | TEXT | Workflow state: 'requested', 'in_review', 'awaiting_implementation', 'awaiting_validation', 'validated', 'superseded' |
| `title` | TEXT | Short, human-friendly title |
| `description` | TEXT | Concise AI-generated summary (max 120 words) |
| `keywords` | TEXT | JSON array of keywords for searchability |
| `date_created` | TEXT | ISO 8601 timestamp when feature was requested |
| `date_fip_approved` | TEXT | Timestamp when FIP passed review (nullable) |
| `date_implemented` | TEXT | Timestamp when implementation was submitted (nullable) |
| `date_validated` | TEXT | Timestamp when feature was validated (nullable) |
| `date_superseded` | TEXT | Timestamp if feature became obsolete (nullable) |
| `commit_hash` | TEXT | Git commit hash where feature was implemented (nullable) |
| `changed_files` | TEXT | JSON array of files modified in implementation (nullable) |

### **`feature_relations` Table**
Stores dependencies and relationships between features:

| Column | Type | Description |
| ------ | ---- | ----------- |
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `feature_id` | TEXT | Source feature ID (foreign key) |
| `relation_type` | TEXT | Relationship type: 'builds_on', 'supersedes', 'refactors', 'fixes' |
| `target_id` | TEXT | Target feature ID (foreign key) |

### **`feature_documents` Table**
Stores feature artifacts (requests, FIPs, ADRs):

| Column | Type | Description |
| ------ | ---- | ----------- |
| `id` | INTEGER PRIMARY KEY | Auto-increment ID |
| `feature_id` | TEXT | Associated feature ID (foreign key) |
| `document_type` | TEXT | Document type: 'request', 'fip', 'adr' |
| `content` | TEXT | Full document content (Markdown) |
| `created_at` | TEXT | ISO 8601 timestamp when document was created |
| `updated_at` | TEXT | ISO 8601 timestamp when document was last modified |

### **Database Benefits**
- **ACID compliance** for data integrity
- **Complex queries** with JOIN operations
- **Efficient indexing** for fast searches
- **Relational integrity** with foreign key constraints
- **Scalability** for large projects with many features
- **Concurrent access** support for future multi-user scenarios