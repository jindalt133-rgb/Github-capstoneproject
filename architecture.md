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

It should scan files such as:

- Python package configuration
- FastAPI application files
- database configuration files
- GitHub Actions workflow files
- pytest configuration
- technical environment configuration files
- other repository files that define runtime, deployment, or build behavior

It does not scan README files or narrative documentation as sources of technical truth.

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

This component is responsible for extracting values for fields such as:

- Application Name
- Language/Runtime
- Frameworks
- Primary Database
- Cloud Provider
- Infrastructure
- Main Branch
- Build Tool
- Deployment Pipeline
- Test Frameworks
- Security Scanning settings
- GitHub Repository
- Current Version
- API Documentation references
- other repository-derived technical fields required by the manifest

Where a value cannot be determined from repository artifacts, the extracted value must be exactly:

- Not Found

### 2.4 Security Filter

The Security Filter guards against writing sensitive data into the generated Markdown manifest.

It checks extracted values and removes or blocks any values that resemble:

- secrets
- tokens
- passwords
- API keys
- credential-like configuration
- environment variables with sensitive naming or values

This component is required before any manifest update is made.

### 2.5 Manifest Reader and Parser

The Manifest Reader and Parser reads the existing Markdown file at:

- docs/technical-app-manifest.md

It identifies:

- section headings
- field labels
- existing values
- narrative sections and human-authored text
- technical field locations that may be updated

It preserves the structure and formatting of the manifest while allowing safe updates to repository-derived technical metadata.

### 2.6 Preservation Layer for Human-Maintained Content

This component ensures that narrative and non-technical values are not overwritten.

It protects fields such as:

- Service Owner
- Business Impact
- Description
- JIRA Board
- On-Call Rotation

It also preserves text outside of the repository-derived technical fields and the existing Markdown organization.

### 2.7 Drift Detector

The Drift Detector compares the repository-derived metadata with the current manifest values.

It checks whether any repository-derived technical fields differ from the manifest and determines whether a synchronization update is needed.

If no technical drift is detected, the manifest should remain unchanged and the process should exit successfully.

### 2.8 Synchronization Orchestrator

The Synchronization Orchestrator is the central logic owner for the automation.

It coordinates the full flow:

- scan repository
- extract metadata
- filter secrets
- read manifest
- preserve human-maintained sections
- compare metadata with manifest
- update repository-derived technical fields
- update Last Updated
- write manifest only when necessary
- complete successfully when there is no drift

### 2.9 Manifest Writer

The Manifest Writer applies safe updates to the Markdown file.

It writes only the repository-derived technical values and the Last Updated value when changes are required.

It must never:

- overwrite human-maintained fields
- modify unrelated files
- rewrite non-technical narrative content
- add unsupported fields or structure outside the required template

### 2.10 GitHub Actions Workflow

The GitHub Actions workflow is the automation mechanism for executing the synchronization process in CI.

It runs the Python automation on repository events and performs the manifest update when drift is detected.

It must also prevent recursive self-triggering after the commit that updates the manifest.

### 2.11 Test Harness

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
7. Drift detection compares repository-derived metadata to the manifest.
8. If drift exists, the synchronization orchestrator updates the allowed technical fields and the Last Updated field.
9. The manifest writer saves the change.
10. If no drift exists, the manifest remains unchanged and the process exits successfully.
11. GitHub Actions executes the workflow and commits the updated manifest when needed.

This data flow ensures that only repository-derived technical values are changed and that no unrelated repository content is touched.

## 4. Metadata Extraction Strategy

The extraction logic should be modular and field-driven.

### 4.1 Extraction by Domain

Metadata should be grouped by domain to keep the logic maintainable:

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

### 4.3 Required Determinism

The extraction process must be deterministic:

- consistent ordering of values
- stable formatting of field names
- repeatable output from the same repository state
- no random or inferred values

This supports idempotent synchronization and snapshot-based testing.

## 5. Authoritative Source Rules

This solution will use repository code and technical configuration as the source of truth.

### 5.1 Allowed Sources

Allowed sources include:

- Python package and technical configuration files
- FastAPI application files
- database settings and configuration files
- GitHub Actions workflow definitions
- pytest configuration
- other technical files required to determine runtime, build, deployment, and testing metadata

### 5.2 Explicitly Disallowed Sources

The following are not sources of technical truth:

- README files
- general documentation pages
- narrative markdown content not tied to actual configuration
- human-written descriptions used for business or operational context

These materials must not drive any repository-derived technical values.

### 5.3 Missing Data Rule

If a technical value is not available from authoritative repository artifacts, the system must write exactly:

- Not Found

This requirement prevents guessing and ensures the manifest remains truthful.

## 6. Manifest Preservation Strategy

The manifest must preserve the existing structure and format of Technical-App-Manifest-v1 while allowing targeted updates to technical fields.

### 6.1 Preservation Rules

The system shall:

- preserve narrative sections and human-written content
- preserve non-technical fields
- preserve ordering and headings
- preserve Markdown formatting
- update only repository-derived technical metadata fields
- keep the overall template structure intact

### 6.2 Protected Fields

The following fields are human-maintained and must never be overwritten by synchronization:

- Service Owner
- Business Impact
- Description
- JIRA Board
- On-Call Rotation

These fields remain subject to human maintenance and should remain untouched unless explicitly changed by a person.

### 6.3 Automatic Field Update

The synchronization process is responsible for updating the field:

- Last Updated

This field is managed automatically by the system and is updated when the manifest is synchronized.

## 7. Drift Detection and Synchronization

Drift detection is the comparison step between the repository-derived metadata model and the current manifest.

### 7.1 Synchronization Logic

The workflow is:

1. extract technical metadata from the repository
2. normalize and filter values
3. read the current manifest
4. compare current manifest values with extracted repository metadata
5. if different, update only the allowed technical fields
6. update Last Updated
7. write the manifest
8. if no technical drift exists, leave the manifest unchanged and return success

### 7.2 Idempotence

The system must be idempotent:

- a second run with no repository changes must not produce a new diff
- repeated synchronization must not create unnecessary file churn
- the manifest must remain stable when there is no drift

### 7.3 Determinism

The process must be deterministic:

- same repository state produces the same manifest output
- stable formatting is preserved
- output ordering remains consistent

## 8. Security and Sensitive Data Handling

Security is a primary architectural constraint.

### 8.1 Sensitive Items to Exclude

The synchronization process must never include:

- secrets
- tokens
- passwords
- API keys
- credential-like values
- sensitive environment variable content

### 8.2 Protection Strategy

The system shall protect metadata using a security filtering stage before manifest writing.

This may include:

- keyword and key-name filtering for secret-like values
- allowlisting only safe metadata fields
- redaction or omission of sensitive configuration values
- rejection of values that are not explicitly permitted for documentation output

### 8.3 Mandatory Constraint

No sensitive data may ever be written to the manifest, commit metadata, logs, or test fixtures.

## 9. GitHub Actions Integration

GitHub Actions is the execution environment for the automated synchronization workflow.

### 9.1 Execution Model

The GitHub Actions workflow will:

- run on repository events defined by the project
- execute the Python synchronization script
- detect manifest drift
- update the manifest when required
- commit the changes back to the repository

### 9.2 Safety Requirement

The workflow must avoid recursive self-triggering after it commits the updated manifest.

This requires guard logic such as:

- skipping workflow runs caused by the bot commit itself
- checking the commit author or message before continuing
- limiting workflow execution to relevant repository changes

The goal is to ensure the automation is safe and does not loop indefinitely.

### 9.3 Scope Control

The workflow must update only the manifest file and must not modify unrelated files in the repository.

## 10. Testing Strategy

The architecture requires a testable solution that supports small-project development without over-engineering.

### 10.1 Unit Tests

Unit tests validate individual components such as:

- repository scanning logic
- metadata extractors
- secret filtering logic
- missing-value handling
- drift comparison rules

### 10.2 Integration Tests

Integration tests verify that the complete workflow works end-to-end against a controlled repository fixture.

This includes:

- repository scan
- metadata extraction
- drift detection
- manifest write
- no-op behavior when no drift exists

### 10.3 Golden/Snapshot Tests

Golden tests verify deterministic output.

They ensure that:

- the same repo state yields the same manifest output
- the format remains consistent with Technical-App-Manifest-v1
- human-maintained fields are preserved as-is
- only repository-derived technical fields change when expected

### 10.4 CI Validation

GitHub Actions is used to run the validation pipeline and confirm the automation works safely in the repository environment.

## 11. Design Assumptions

This architecture assumes:

- the project is a small Python repository with limited scope
- the technical manifest is a single Markdown file at a fixed path
- the repository contains enough technical configuration to support reliable metadata extraction
- human-maintained narrative content should be preserved and protected from automated overwrite
- the project does not require multi-service deployment or remote microservice coordination
- GitHub Actions is the designated automation platform

## 12. Architectural Decisions

### Decision 1: Single Python automation module

The solution will be implemented as a small Python application with modular internal components rather than separate services.

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

### Decision 7: Workflow recursion is prevented

The workflow includes guard logic to avoid repeating sync commits indefinitely.

### Decision 8: Determinism and idempotence are required

The output must be stable and safe when the repository has not changed.

## 13. Scope Boundary

This architecture intentionally does not introduce functionality beyond the approved requirements.

It does not include:

- alternate manifest formats
- configurable manifest paths
- external microservices
- README-based metadata inference
- broad document rewriting beyond the required manifest
- unsupported automation beyond GitHub Actions workflow execution

The architecture remains focused on the required solution: synchronizing repository-derived technical metadata into the manifest while preserving human-maintained content and maintaining safe, deterministic automation.
