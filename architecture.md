# Architecture: Automated Technical Documentation Sync

## 1. Architecture Overview

This solution is a small, practical Python-based automation workflow for synchronizing repository-derived technical metadata into the Markdown manifest at:

- docs/technical-app-manifest.md

The architecture is intentionally kept simple and implementable for a small Python project. It does not introduce separate services or distributed components. Instead, it uses a single Python application with modular internal components that run locally for testing and in GitHub Actions for automation.

The system responsibilities are:

- scan repository files that are authoritative for technical metadata
- extract technical metadata from those files
- sanitize secret and credential-like values
- read the existing manifest
- preserve human-maintained narrative sections and non-technical fields
- update only repository-derived technical metadata
- detect drift between repository metadata and manifest content
- update the Last Updated field during synchronization
- write the manifest only when technical drift is detected
- remain deterministic and idempotent
- support automated validation in CI
- avoid recursive GitHub Actions re-triggering

The manifest must follow the Technical-App-Manifest-v1 structure and formatting. The repository code and technical configuration are the source of truth. README files and general project documentation are not considered authoritative for technical metadata.

## 2. Components and Responsibilities

### 2.1 Repository Scanner

The Repository Scanner is responsible for traversing the repository and finding files that may contain technical metadata.

It scans only the repository files that are allowed to be authoritative technical sources. It does not inspect README files or general project documentation as a source of technical truth.

### 2.2 Authoritative Source Rules

This layer defines which files are valid sources for technical metadata and which are not.

It ensures that only repository code and technical configuration are used as sources of truth.

This layer is responsible for:

- allowing only technical or configuration files as valid sources
- rejecting README files and general documentation as authoritative sources
- standardizing the set of supported metadata sources
- keeping extraction deterministic and consistent

### 2.3 Metadata Extractor

The Metadata Extractor reads the authoritative files and converts repository state into a normalized metadata model.

This component is responsible for extracting values for fields required by the manifest. It must normalize values before they are stored and compared.

### 2.4 Normalization and Comparison Layer

The Normalization and Comparison Layer standardizes metadata values before they are compared with the manifest.

It is responsible for:

- lowercasing values when appropriate
- trimming leading/trailing whitespace
- normalizing list ordering for multi-value fields
- preserving consistent formatting for values such as branch names, environment names, and URLs
- comparing repository-derived values and manifest values field-by-field after normalization

This ensures drift detection is deterministic and repeatable.

### 2.5 Security Filter

The Security Filter guards against writing sensitive data into the generated Markdown manifest.

It checks extracted values and removes or blocks any values associated with names or patterns such as:

- SECRET
- PASSWORD
- TOKEN
- API_KEY
- CREDENTIAL
- PRIVATE_KEY
- and similar credential-like identifiers

Environment variable names may be documented when appropriate, but their values must never be written to the manifest. If a field is intentionally excluded because it is sensitive, the technical field value for that field must be recorded as Not Found where the field contract requires a value.

### 2.6 Manifest Reader and Parser

The Manifest Reader and Parser reads the existing Markdown file at:

- docs/technical-app-manifest.md

It identifies:

- section headings
- field labels
- existing values
- narrative sections and human-authored text
- technical field locations that may be updated

It preserves the structure and formatting of the manifest while allowing safe updates to repository-derived technical metadata.

### 2.7 Preservation Layer for Human-Maintained Content

This component ensures that narrative and non-technical values are not overwritten.

It protects a fixed allowlist of repository-derived technical fields that may be synchronized and a fixed blocklist of human-maintained fields that must never be touched.

Protected human-maintained fields include:

- Service Owner
- Business Impact
- Description
- JIRA Board
- On-Call Rotation

It also preserves text outside of the repository-derived technical fields and the existing Markdown organization.

### 2.8 Drift Detector

The Drift Detector compares normalized repository-derived metadata with the normalized manifest values.

It checks whether any repository-derived technical fields differ from the manifest and determines whether a synchronization update is needed.

If no technical drift is detected, the manifest remains unchanged and the process exits successfully.

### 2.9 Synchronization Orchestrator

The Synchronization Orchestrator is the central logic owner for the automation.

It coordinates the full flow:

- scan repository
- extract metadata
- normalize values
- filter secrets
- read manifest
- validate protected field boundaries
- compare metadata with manifest
- update repository-derived technical fields only
- update Last Updated
- verify resulting diff
- write manifest only when a real change exists
- complete successfully when there is no drift

### 2.10 Manifest Writer

The Manifest Writer applies safe updates to the Markdown file.

It updates only explicitly targeted technical fields and the Last Updated value. It does not regenerate the whole document.

It must never:

- overwrite human-maintained fields
- modify unrelated files
- rewrite non-technical narrative content
- add unsupported fields or structure outside the required template

### 2.11 GitHub Actions Workflow

The GitHub Actions workflow is the automation mechanism for executing the synchronization process in CI.

It runs the Python automation on repository events, detects manifest drift, updates the manifest when required, and commits the updated file only when it has a real change.

It prevents recursive self-triggering by detecting the automation-generated commit and skipping synchronization for that commit.

### 2.12 Test Harness

The Test Harness provides automated verification across the solution.

It supports:

- unit tests
- integration tests
- golden/snapshot tests
- CI validation

This ensures the result is deterministic, idempotent, and safe.

## 3. Data Flow

The data flow is intentionally simple and linear:

1. Repository scan begins.
2. The scanner identifies authoritative technical files only.
3. The metadata extractor reads those files and produces normalized technical metadata.
4. The security filter removes secret or credential-like values.
5. The existing manifest is read and parsed.
6. Human-maintained narrative and non-technical fields are preserved.
7. Metadata and manifest values are normalized for comparison.
8. Drift detection compares repository-derived metadata to the manifest field-by-field.
9. If drift exists, the synchronization orchestrator updates only the allowed technical fields and Last Updated.
10. The manifest writer verifies the resulting diff and writes the file only when an actual change exists.
11. If no drift exists, the manifest remains unchanged and the process exits successfully.
12. GitHub Actions executes the workflow, commits only when a real manifest change exists, and skips automation-generated commits to avoid loops.

This data flow ensures that only repository-derived technical values are changed and that no unrelated repository content is touched.

## 4. Metadata Extraction Strategy

The extraction logic is modular and field-driven.

### 4.1 Extraction by Domain

Metadata is grouped by domain to keep the logic maintainable:

- application identity
- runtime and language
- framework and libraries
- database configuration
- deployment configuration
- CI/CD metadata
- build pipeline details
- testing and quality metadata
- repository metadata

### 4.2 Extraction Rules

Each extractor should:

- read only authoritative technical sources
- normalize the extracted value into a consistent format
- produce a structured value for comparison and writing
- return Not Found when no valid repository value exists
- return an explicit error when an authoritative configuration file is unreadable or malformed

### 4.3 Determinism and Repeatability

The extraction process must be deterministic:

- consistent ordering of values
- stable formatting of field names
- repeatable output from the same repository state
- no random or inferred values

This supports idempotent synchronization and snapshot-based testing.

## 5. Field-to-Source Mapping

The system uses an explicit field catalog to map each repository-derived manifest field to its authoritative source, extraction method, normalization rule, and fallback behavior.

| Manifest Field | Authoritative Source | Extraction Method | Normalization Rule | Fallback Behavior |
|---|---|---|---|---|
| Application Name | repository metadata / package metadata / app entrypoints | parse project metadata and app identifiers | trim whitespace; canonical casing for display | Not Found |
| Language/Runtime | Python project configuration and runtime files | parse Python version/runtime metadata | normalize runtime string; remove duplicate whitespace | Not Found |
| Frameworks | FastAPI and Python dependency configuration | parse dependency metadata and framework imports | stable list ordering; lowercase compare values | Not Found |
| Primary Database | database config and application config | inspect DB configuration settings | normalize database name; single canonical value | Not Found |
| Cloud Provider | deployment config / infrastructure files | inspect provider configuration | lowercase provider name; single canonical value | Not Found |
| Infrastructure | IaC / deployment configuration | parse infrastructure config | normalize whitespace; single canonical string | Not Found |
| Main Branch | repository settings / branch config | read default branch configuration | normalize branch names; lowercase when appropriate | Not Found |
| Build Tool | project config and CI workflow | inspect build-related config | canonicalize tool names | Not Found |
| Critical Env Variables | technical env config and application config | identify non-sensitive environment keys and safe documented config | stable sorted list; exclude sensitive values | Not Found |
| Deployment Pipeline | GitHub Actions workflow files | parse workflow jobs and actions | normalize workflow names; stable output | Not Found |
| Test Frameworks | pytest config and test tooling files | inspect pytest and related config | sort and canonicalize names | Not Found |
| Code Coverage Goal | pytest config / tooling config | parse coverage configuration | normalize numeric or percentage value | Not Found |
| Security Scanning | GitHub Actions and repo security tooling | inspect scan workflows or tool config | canonicalize scanner name | Not Found |
| Observation/Logging | app config and observability settings | inspect logging and monitoring config | canonicalize names and values | Not Found |
| GitHub Repository | git remote metadata / repo metadata | read remote or repository metadata | canonical URL / repo slug | Not Found |
| API Documentation | app routes / docs config / repo config | detect OpenAPI docs or doc endpoints | canonicalize URL/path value | Not Found |
| JIRA Board | human-maintained field; not repository-derived | not automatically updated | preserved as-is | protected field remains unchanged |
| On-Call Rotation | human-maintained field; not repository-derived | not automatically updated | preserved as-is | protected field remains unchanged |
| Current Version | package metadata / release metadata / config | parse version metadata | normalize semantic version format | Not Found |
| Last Updated | synchronization process | write current UTC timestamp at sync time | UTC ISO-8601 format: YYYY-MM-DDTHH:MM:SSZ | managed by sync process |
| Service Owner | human-maintained field; not repository-derived | not automatically updated | preserved as-is | protected field remains unchanged |
| Business Impact | human-maintained field; not repository-derived | not automatically updated | preserved as-is | protected field remains unchanged |
| Description | human-maintained field; not repository-derived | not automatically updated | preserved as-is | protected field remains unchanged |

This field catalog is the implementation contract for the synchronization system and defines which values are safe to update, which values are protected, and which values must be represented as Not Found when unavailable.

## 6. Authoritative Source Rules

This solution uses repository code and technical configuration as the source of truth.

### 6.1 Allowed Sources

Allowed sources include:

- Python package and technical configuration files
- FastAPI application files
- database settings and configuration files
- GitHub Actions workflow definitions
- pytest configuration
- other technical files required to determine runtime, build, deployment, and testing metadata

### 6.2 Explicitly Disallowed Sources

The following are not sources of technical truth:

- README files
- general documentation pages
- narrative markdown content not tied to actual configuration
- human-written descriptions used for business or operational context

These materials must not drive any repository-derived technical values.

### 6.3 Missing Data Rule

If a technical value is not available from authoritative repository artifacts, the system writes exactly:

- Not Found

If a field is intentionally excluded because it is sensitive, the field value must also be represented as Not Found if the field contract requires a value.

### 6.4 Invalid or Unreadable Repository State

If an authoritative configuration file is unreadable, malformed, or cannot be parsed, the system reports an explicit error and does not write a partially generated manifest.

## 7. Manifest Preservation Strategy

The manifest must preserve the existing structure and format of Technical-App-Manifest-v1 while allowing targeted updates to the repository-derived technical fields.

### 7.1 Preservation Rules

The system shall:

- preserve narrative sections and human-written content
- preserve non-technical fields
- preserve ordering and headings
- preserve Markdown formatting
- update only repository-derived technical metadata fields
- keep the overall template structure intact
- use section-aware and field-level updates; do not regenerate the full document

### 7.2 Protected Fields and Allowlist

The synchronization process maintains an explicit allowlist of repository-derived fields that may be updated and a protected blocklist of human-maintained fields that must never be modified.

Allowed technical fields include only those values derived from repository metadata, such as:

- Application Name
- Language/Runtime
- Frameworks
- Primary Database
- Cloud Provider
- Infrastructure
- Main Branch
- Build Tool
- Critical Env Variables
- Deployment Pipeline
- Test Frameworks
- Code Coverage Goal
- Security Scanning
- Observation/Logging
- GitHub Repository
- API Documentation
- Current Version
- Last Updated

Protected human-maintained fields include:

- Service Owner
- Business Impact
- Description
- JIRA Board
- On-Call Rotation

Before writing any manifest update, the system validates that only allowlisted technical fields will change and that no protected fields are included in the proposed change set.

### 7.3 Last Updated Format

Last Updated is managed by the synchronization process and must use UTC ISO-8601 timestamp format:

- YYYY-MM-DDTHH:MM:SSZ

It is updated only when the manifest is actually synchronized because technical metadata changed.

## 8. Drift Detection and Synchronization

Drift detection is the comparison step between normalized repository-derived metadata and the normalized current manifest values.

### 8.1 Normalization Rules

Both extracted metadata and manifest values are normalized before comparison.

Normalization rules include:

- trim whitespace
- normalize casing where appropriate
- normalize list ordering for multi-value fields
- standardize separators and formatting
- apply consistent comparison rules for URLs, branch names, and version strings

### 8.2 Synchronization Logic

The workflow is:

1. extract technical metadata from the repository
2. normalize and filter values
3. read the current manifest
4. normalize manifest values for comparison
5. compare the values field-by-field
6. if different, update only the allowed technical fields
7. update Last Updated
8. verify the resulting diff
9. write the manifest only when a real change exists
10. if no drift exists, leave the manifest unchanged and return success

### 8.3 Idempotence

The system must be idempotent:

- a second run with no repository changes must not produce a new diff
- repeated synchronization must not create unnecessary file churn
- the manifest must remain stable when there is no drift

### 8.4 Determinism

The process must be deterministic:

- same repository state produces the same manifest output
- stable formatting is preserved
- output ordering remains consistent
- drift decisions are based only on normalized values after all required filtering is applied

## 9. Security and Sensitive Data Handling

Security is a primary architectural constraint.

### 9.1 Sensitive Items to Exclude

The synchronization process must never include:

- secrets
- tokens
- passwords
- API keys
- credential-like values
- sensitive environment variable content

It treats values associated with names such as:

- SECRET
- PASSWORD
- TOKEN
- API_KEY
- CREDENTIAL
- PRIVATE_KEY
- and similar credential patterns

as sensitive.

### 9.2 Protection Strategy

The system shall protect metadata using a security filtering stage before manifest writing.

This includes:

- keyword and key-name filtering for secret-like values
- allowlisting only safe metadata fields
- redaction or omission of sensitive configuration values
- rejection of values that are not explicitly permitted for documentation output
- preserving environment variable names only when they are safe to document, while never writing their values

If a field is intentionally excluded because it is sensitive, the system uses Not Found for that field when the field contract requires a value.

### 9.3 Mandatory Constraint

No sensitive data may ever be written to the manifest, commit metadata, logs, or test fixtures.

## 10. GitHub Actions Integration

GitHub Actions is the execution environment for the automated synchronization workflow.

### 10.1 Execution Model

The GitHub Actions workflow will:

- run on repository events defined by the project
- execute the Python synchronization script
- detect manifest drift
- update the manifest when required
- verify the resulting diff
- commit the changes back to the repository only when a real change exists

### 10.2 Safety Requirement and Recursive Protection

The workflow must avoid recursive self-triggering after it commits the updated manifest.

The concrete mechanism is:

- detect whether the current commit was created by the automation bot or by the sync process itself
- skip synchronization for that automation-generated commit

This is the required anti-recursion guard for the workflow. The automation must not run again for the commit it just created.

### 10.3 Scope Control

The workflow must update only the manifest file and must not modify unrelated files in the repository.

### 10.4 No-Op Behavior

If there is no drift:

- do not modify the manifest
- do not create a commit
- exit successfully

If drift exists:

- update only allowed technical fields
- update Last Updated
- verify the resulting diff
- commit only when an actual change exists

## 11. Error Handling

The workflow and synchronization logic define explicit behavior for predictable failure conditions.

### 11.1 Failure Modes

The system handles the following failure modes:

- missing files
- unreadable files
- malformed configuration
- malformed manifest
- unsupported repository state
- failed metadata extraction
- failed manifest update

### 11.2 Required Behavior

On failure:

- report the error explicitly
- do not write the manifest when the intermediate metadata state is invalid
- do not partially generate or partially update the manifest
- exit with a non-zero status if the required sync cannot be completed safely

This is essential to prevent inconsistent documentation or untrusted manifest state.

## 12. Testing Strategy

The architecture requires a testable solution that supports small-project development without over-engineering.

### 12.1 Unit Tests

Unit tests validate individual components such as:

- repository scanning logic
- metadata extractors
- normalization rules
- secret filtering logic
- missing-value handling
- drift comparison rules
- manifest parsing and update logic

### 12.2 Integration Tests

Integration tests verify that the complete workflow works end-to-end against a controlled repository fixture.

This includes:

- repository scan
- metadata extraction
- normalization
- drift detection
- manifest write
- no-op behavior when no drift exists
- protected-field preservation

### 12.3 Golden/Snapshot Tests

Golden tests verify deterministic output.

They ensure that:

- the same repo state yields the same manifest output
- the format remains consistent with Technical-App-Manifest-v1
- human-maintained fields are preserved as-is
- only repository-derived technical fields change when expected
- Last Updated uses the expected UTC ISO-8601 format

### 12.4 CI Validation

GitHub Actions is used to run the validation pipeline and confirm the automation works safely in the repository environment.

The concrete CI test matrix includes:

- normal metadata extraction
- missing metadata → Not Found
- protected-field preservation
- secret filtering
- deterministic output
- idempotent repeated execution
- drift detection
- no-drift behavior
- manifest formatting using a golden/snapshot test
- CI recursion protection

## 13. Design Assumptions

This architecture assumes:

- the project is a small Python repository with limited scope
- the technical manifest is a single Markdown file at a fixed path
- the repository contains enough technical configuration to support reliable metadata extraction
- human-maintained narrative content should be preserved and protected from automated overwrite
- the project does not require multi-service deployment or remote microservice coordination
- GitHub Actions is the designated automation platform
- the manifest structure is defined by Technical-App-Manifest-v1 and will remain stable for this capstone

## 14. Architectural Decisions

### Decision 1: Single Python automation module

The solution is implemented as a small Python application with modular internal components rather than separate services.

This keeps the design practical for a small project while satisfying the requirements.

### Decision 2: Repository and config files as the only source of technical truth

README and general documentation are not used as authoritative sources for technical metadata.

### Decision 3: Manifest update is field-scoped, not full-document regeneration

The system updates only repository-derived technical metadata and does not overwrite human-maintained narrative or non-technical content.

### Decision 4: Missing values are explicit and truthful

If a value cannot be determined, the system records exactly Not Found rather than guessing.

### Decision 5: Security filtering is mandatory

Sensitive values are always excluded or masked before generating the manifest.

### Decision 6: GitHub Actions performs automation and commit logic

The workflow is the execution mechanism for synchronization and commit automation.

### Decision 7: Workflow recursion is prevented by automation-commit detection

The workflow skips synchronization when the current commit was created by the automation itself.

### Decision 8: Determinism and idempotence are required

The output must be stable and safe when the repository has not changed.

### Decision 9: Last Updated uses UTC ISO-8601

The system writes Last Updated in the format YYYY-MM-DDTHH:MM:SSZ and updates it only when a real technical change has been synchronized.

## 15. Scope Boundary

This architecture intentionally does not introduce functionality beyond the approved requirements.

It does not include:

- alternate manifest formats
- configurable manifest paths
- external microservices
- README-based metadata inference
- broad document rewriting beyond the required manifest
- unsupported automation beyond GitHub Actions workflow execution

The architecture remains focused on the required solution: synchronizing repository-derived technical metadata into the manifest while preserving human-maintained content and maintaining safe, deterministic automation.
