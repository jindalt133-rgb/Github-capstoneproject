# Requirements: Automated Technical Documentation Sync

## 1. Purpose

The purpose of this project is to automatically synchronize the repository-derived technical metadata in the technical application manifest with the current state of the application repository, while preserving human-maintained narrative and operational information.

The solution shall ensure that the technical documentation remains current without requiring manual updates, while protecting sensitive data and avoiding unintended changes to unrelated repository content.

## 2. Scope

This solution applies to the Task Management API application and its repository. It is responsible for generating and updating the Markdown technical application manifest located at:

- docs/technical-app-manifest.md

The synchronization process shall operate on this manifest only and shall not modify unrelated files in the repository.

## 3. Functional Requirements

### 3.1 Manifest Location and Format

FR-1. The system shall maintain the technical application manifest as a Markdown file at the fixed path:

- docs/technical-app-manifest.md

FR-2. The manifest shall follow the Technical-App-Manifest-v1 structure and formatting.

FR-3. The manifest shall preserve the existing Technical-App-Manifest-v1 layout and section ordering unless the synchronization process updates technical metadata values within that structure.

### 3.2 Required Manifest Sections and Fields

FR-4. The manifest shall include the following sections and fields:

- Executive Summary
  - Application Name
  - Service Owner
  - Business Impact
  - Description

- System Architecture & Tech Stack
  - Language/Runtime
  - Frameworks
  - Primary Database
  - Cloud Provider
  - Infrastructure

- Integration & Dependencies
  - Upstream Dependencies
  - Downstream Consumers
  - External APIs

- Technical Configuration
  - Main Branch
  - Build Tool
  - Critical Env Variables
  - Deployment Pipeline

- Quality & Compliance
  - Test Frameworks
  - Code Coverage Goal
  - Security Scanning
  - Observation/Logging

- Documentation & Resources
  - GitHub Repository
  - API Documentation
  - JIRA Board
  - On-Call Rotation

- Deployment Status
  - Current Version
  - Last Updated

FR-5. The synchronization process shall update only those technical metadata fields that can be derived from repository information.

### 3.3 Repository Metadata Extraction

FR-6. The system shall inspect the application repository and detect technical metadata using authoritative repository artifacts only.

FR-7. Authoritative sources for technical metadata shall include:

- application code
- Python package and project configuration
- database configuration
- GitHub Actions workflow files
- pytest configuration and related test configuration
- other technical configuration files required to determine repository state

FR-8. README files, narrative documentation, and other non-authoritative documentation shall not be treated as primary sources for repository-derived technical information.

FR-9. The synchronization process shall not use unsupported assumptions or guesses when a technical value cannot be reliably determined from repository artifacts.

### 3.4 Missing Data Handling

FR-10. For any technical metadata field that cannot be determined from repository artifacts, the manifest shall contain the exact value:

- Not Found

FR-11. The system shall not guess, infer, or invent values for missing technical metadata.

### 3.5 Preservation of Human-Maintained Fields

FR-12. Human-maintained fields shall be preserved and never overwritten by the synchronization process.

FR-13. The following fields shall remain under human control and shall not be modified by automated synchronization:

- Service Owner
- Business Impact
- Description
- JIRA Board
- On-Call Rotation

FR-14. The synchronization process shall preserve narrative content, non-technical sections, formatting, structure, and overall template layout.

FR-15. The synchronization process shall only update technical metadata fields that are repository-derived and permitted to be automated.

### 3.6 Last Updated Behavior

FR-16. The Last Updated field in the Deployment Status section shall be managed by the synchronization process.

FR-17. When the manifest is synchronized, the Last Updated field shall be updated to the current timestamp or equivalent synchronization time value.

FR-18. The synchronization process shall not require a human to manually update Last Updated.

### 3.7 Drift Detection and Manifest Updates

FR-19. The system shall detect differences between the repository-derived technical metadata and the existing manifest content.

FR-20. When technical drift is detected, the system shall generate and apply the updated repository-derived metadata in docs/technical-app-manifest.md.

FR-21. When no technical drift is detected, the manifest shall remain unchanged and the synchronization process shall complete successfully.

FR-22. The synchronization process shall be idempotent so that repeated execution with no repository changes does not create unnecessary manifest modifications.

### 3.8 Change Scope Boundary

FR-23. The synchronization process shall never modify unrelated files in the repository.

FR-24. The process shall limit all file changes to the technical application manifest at:

- docs/technical-app-manifest.md

### 3.9 Security and Sensitive Data Handling

FR-25. The synchronization process shall never include secrets, tokens, passwords, API keys, or other sensitive values in generated documentation.

FR-26. Sensitive values detected in repository configuration or environment files shall be excluded, redacted, or omitted from the manifest output.

FR-27. The system shall not expose credentials or secret-like values in generated manifest content, logs, or test artifacts.

### 3.10 GitHub Actions Workflow Behavior

FR-28. The GitHub Actions workflow shall execute the synchronization process automatically when repository metadata changes.

FR-29. When the workflow updates the manifest, it shall commit the manifest changes automatically.

FR-30. The GitHub Actions workflow shall include logic to avoid repeated, self-triggering loops indefinitely when it commits an updated manifest.

FR-31. The workflow shall prevent infinite automation cycles by using safe commit conditions or guard logic to avoid retriggering itself after the manifest update.

### 3.11 Testability

FR-32. The synchronization process shall be testable through automated validation.

FR-33. The project shall include tests covering:

- unit tests for extraction logic
- integration tests for repository-to-manifest synchronization
- CI validation for workflow behavior
- golden/snapshot tests for manifest output and formatting

## 4. Non-Functional Requirements

### 4.1 Accuracy

NFR-1. The generated technical metadata shall accurately reflect the repository state.

NFR-2. The tool shall prioritize authoritative repository data over assumptions or manual estimates.

### 4.2 Safety

NFR-3. The system shall protect sensitive data and shall not expose secrets in documentation.

NFR-4. The solution shall restrict its changes to the manifest file and avoid repository-wide modifications.

### 4.3 Determinism

NFR-5. Given the same repository state and same template, the output manifest shall be deterministic.

NFR-6. The process shall produce stable results without random or non-repeatable field generation.

### 4.4 Idempotence

NFR-7. Re-running the synchronization process without repository drift shall not trigger changes to the manifest.

NFR-8. The process shall avoid unnecessary diffs and repeated commits caused by unchanged content.

### 4.5 Maintainability

NFR-9. The synchronization logic shall be structured to support clear unit and integration testing.

NFR-10. The project shall support future extension of metadata extraction without disrupting the manifest template structure.

### 4.6 Readability and Documentation Quality

NFR-11. The generated manifest shall remain readable, consistent, and aligned with the Technical-App-Manifest-v1 template.

NFR-12. Human-maintained sections shall remain understandable and intact after automated synchronization.

## 5. Acceptance Criteria

AC-1. The repository contains a technical application manifest at docs/technical-app-manifest.md in Markdown format.

AC-2. The manifest follows the Technical-App-Manifest-v1 structure and includes all required sections and fields.

AC-3. Repository-derived technical fields are populated from authoritative repository artifacts.

AC-4. If a technical field cannot be determined from the repository, the manifest contains Not Found instead of a guessed value.

AC-5. Human-maintained fields such as Service Owner, Business Impact, Description, JIRA Board, and On-Call Rotation are preserved and not overwritten during synchronization.

AC-6. The Last Updated field is updated automatically by the synchronization process whenever the manifest is synchronized.

AC-7. The synchronization process modifies only docs/technical-app-manifest.md and does not change unrelated repository files.

AC-8. When no technical drift is present, the synchronization process completes successfully without modifying the manifest.

AC-9. When drift is detected, the technical metadata in docs/technical-app-manifest.md is updated automatically.

AC-10. The GitHub Actions workflow updates and commits the manifest automatically when drift is detected.

AC-11. The GitHub Actions workflow includes guard logic to prevent infinite self-triggering loops after committing the manifest update.

AC-12. Secrets and sensitive values are excluded from generated manifest content.

AC-13. Automated tests validate extraction logic, integration flow, CI behavior, and manifest output consistency.

## 6. Out of Scope

The following are explicitly out of scope for this capstone project:

- creating a configurable manifest path or alternate file format
- modifying unrelated repository documentation or application files
- using README or other narrative docs as authoritative technical metadata sources
- implementing arbitrary new documentation templates beyond Technical-App-Manifest-v1
- implementing source code changes beyond the synchronization logic and test coverage required for the defined requirements

## 7. Definition of Done

The project is complete when all acceptance criteria are satisfied, the manifest remains aligned with the Technical-App-Manifest-v1 template, human-maintained fields are protected, no unrelated files are modified, branch automation is safe and non-recursive, and the synchronization behavior is validated through automated tests.
