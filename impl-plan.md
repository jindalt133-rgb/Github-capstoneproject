# Implementation Plan: Automated Technical Documentation Sync

## 1. Objective

This implementation plan defines the practical, dependency-ordered work required to implement the approved architecture for the Automated Technical Documentation Sync solution.

The solution is intentionally limited to a small Python project and follows the approved design decisions from the user story, requirements, architecture, and design review.

The implementation must:

- maintain the technical manifest at docs/technical-app-manifest.md
- preserve the Technical-App-Manifest-v1 structure and formatting
- use repository code and technical configuration as the source of truth
- treat README and general documentation as non-authoritative
- represent missing technical values as Not Found
- preserve human-maintained fields and narrative content
- update only repository-derived technical metadata
- manage Last Updated automatically in UTC ISO-8601 format
- filter sensitive values before writing
- support deterministic and idempotent behavior
- run in GitHub Actions safely without recursive self-triggering
- remain testable through unit, integration, golden/snapshot, and CI validation

## 2. Recommended Execution Order

1. Project skeleton and metadata contract
2. Repository scanning and source detection
3. Extraction and normalization
4. Secret filtering and missing-data rules
5. Manifest parsing and protected-field logic
6. Drift detection and Last Updated
7. Orchestration and CLI entrypoint
8. Tests and golden validation
9. GitHub Actions workflow and recursion prevention
10. Final verification

## 3. Dependency Summary

The critical path is:

- project setup
- field catalog
- source detection
- extraction
- normalization
- filtering
- manifest parsing/update
- drift detection
- orchestration
- workflow automation
- final verification

This order ensures that the implementation is built on the approved architecture without introducing unnecessary abstractions or premature infrastructure.

## 4. Implementation Tasks

### Task ID: P0-01
Priority: Critical
Task description:
Set up the minimal Python project structure and configuration needed for a small, testable automation tool. Define the package layout, dependency management, and script entrypoint for local execution and GitHub Actions.

Files/components affected:
- pyproject.toml or equivalent
- src/doc_sync/
- tests/
- .github/workflows/

Dependencies:
- None

Expected outcome:
A working Python project skeleton exists with a clear modular layout and a consistent entrypoint for local runs and CI.

Testing required:
- basic import/test discovery validation
- CI smoke check

Blocked:
No

### Task ID: P0-02
Priority: Critical
Task description:
Define the technical metadata contract and field catalog for the manifest. This includes the field-to-source mapping, normalization rules, fallback behavior, and the protected field list.

Files/components affected:
- src/doc_sync/field_catalog.py
- src/doc_sync/models.py
- src/doc_sync/config.py

Dependencies:
- P0-01

Expected outcome:
A clear implementation contract exists for each manifest field, including:
- authoritative source
- extraction method
- normalization rule
- fallback behavior
- protection rules for human-maintained fields

Testing required:
- unit tests for catalog integrity
- validation of protected-field registry

Blocked:
No

### Task ID: P0-03
Priority: Critical
Task description:
Define the repository source detection and authoritative-source rules. Identify which repository files are valid technical sources and which are disallowed, explicitly excluding README and general documentation.

Files/components affected:
- src/doc_sync/source_registry.py
- src/doc_sync/repo_scan.py

Dependencies:
- P0-01
- P0-02

Expected outcome:
The system can identify authoritative technical files only and ignore README/docs as sources of truth.

Testing required:
- unit tests for source allowlist/blocklist
- fixture-based repo scanning tests

Blocked:
No

### Task ID: P0-04
Priority: Critical
Task description:
Implement basic repository scan logic to locate allowed technical files and collect candidate inputs for extraction.

Files/components affected:
- src/doc_sync/repo_scan.py
- src/doc_sync/filesystem.py

Dependencies:
- P0-03

Expected outcome:
The project can scan the repository and return a set of valid technical files for parsing.

Testing required:
- unit tests for file discovery
- integration tests with fixture repos

Blocked:
No

### Task ID: P1-05
Priority: High
Task description:
Implement metadata extraction for repository-derived fields by domain. Extract values from application code, Python config, workflow files, pytest config, and technical configuration files.

Files/components affected:
- src/doc_sync/extractors/
- src/doc_sync/extractors/runtime.py
- src/doc_sync/extractors/deps.py
- src/doc_sync/extractors/config.py
- src/doc_sync/extractors/workflows.py
- src/doc_sync/extractors/tests.py

Dependencies:
- P0-04

Expected outcome:
The system produces a structured metadata model for all repository-derived manifest fields.

Testing required:
- unit tests for each extractor
- integration tests against sample repo fixture

Blocked:
No

### Task ID: P1-06
Priority: High
Task description:
Implement normalization for extracted values and manifest values. Normalize case, whitespace, list ordering, formatting, and version or URL formatting so drift detection is consistent and deterministic.

Files/components affected:
- src/doc_sync/normalize.py
- src/doc_sync/comparison.py

Dependencies:
- P0-02
- P1-05

Expected outcome:
Repository metadata and manifest values are represented in a comparable canonical form.

Testing required:
- unit tests for normalization rules
- tests for list ordering and whitespace consistency

Blocked:
No

### Task ID: P1-07
Priority: High
Task description:
Implement secret and sensitive-value filtering before manifest writing. Use explicit sensitive patterns and key-name detection for SECRET, PASSWORD, TOKEN, API_KEY, CREDENTIAL, PRIVATE_KEY, and similar cases.

Files/components affected:
- src/doc_sync/security.py
- src/doc_sync/validators.py

Dependencies:
- P1-05
- P0-02

Expected outcome:
Any sensitive value is removed or omitted from the generated metadata. Sensitive fields are represented as Not Found when required by contract.

Testing required:
- unit tests for secret filtering
- integration tests for sensitive configuration values

Blocked:
No

### Task ID: P1-08
Priority: High
Task description:
Implement missing-value handling and invalid-data rules. Missing repository values become Not Found; empty technical values become Not Found where appropriate; parse failures and unreadable authoritative config files raise explicit errors.

Files/components affected:
- src/doc_sync/values.py
- src/doc_sync/errors.py
- src/doc_sync/extractors/

Dependencies:
- P1-05
- P1-06
- P1-07

Expected outcome:
The system distinguishes between:
- missing values
- empty values
- sensitive exclusions
- invalid or unreadable repository inputs

Testing required:
- unit tests for Not Found behavior
- error-handling tests for malformed config

Blocked:
No

### Task ID: P1-09
Priority: High
Task description:
Implement manifest parsing and field-level update logic using section-aware Markdown updates. Do not regenerate the entire document.

Files/components affected:
- src/doc_sync/manifest.py
- src/doc_sync/manifest_update.py

Dependencies:
- P0-02
- P1-06
- P1-08

Expected outcome:
The system can:
- read the current manifest
- identify target fields
- preserve all non-target content
- update only explicitly allowed technical fields
- preserve headings, order, narrative, and formatting

Testing required:
- unit tests for parser behavior
- snapshot tests for field-level update correctness
- protection tests for human fields

Blocked:
No

### Task ID: P1-10
Priority: High
Task description:
Implement protected field enforcement. Validate the change set before writing to ensure only allowlisted repository-derived technical fields are updated and human-maintained fields are never modified.

Files/components affected:
- src/doc_sync/manifest_update.py
- src/doc_sync/validators.py

Dependencies:
- P0-02
- P1-09

Expected outcome:
The system refuses or blocks any manifest update that would touch protected human-maintained fields.

Testing required:
- unit tests for protected-field validation
- end-to-end tests for manifest preservation

Blocked:
No

### Task ID: P1-11
Priority: High
Task description:
Implement drift detection and no-drift behavior. Compare normalized repository metadata against normalized manifest values and decide whether a synchronization change is necessary.

Files/components affected:
- src/doc_sync/drift.py
- src/doc_sync/sync.py

Dependencies:
- P1-06
- P1-09
- P1-10

Expected outcome:
The tool can determine whether technical drift exists and can return a clean no-op result when no change is needed.

Testing required:
- unit tests for drift detection
- integration tests for no-drift execution
- idempotence tests

Blocked:
No

### Task ID: P1-12
Priority: High
Task description:
Implement Last Updated handling. Use UTC ISO-8601 format and update it only when the manifest is actually synchronized because technical metadata changed.

Files/components affected:
- src/doc_sync/manifest_update.py
- src/doc_sync/sync.py

Dependencies:
- P1-09
- P1-11

Expected outcome:
Last Updated is automatically managed by the synchronization process and is not written during no-op runs.

Testing required:
- unit tests for timestamp formatting
- integration tests verifying update only on drift

Blocked:
No

### Task ID: P1-13
Priority: High
Task description:
Implement the synchronization orchestration layer. This is the main workflow that:
- scans repo
- extracts metadata
- filters sensitive values
- reads manifest
- compares values
- updates only allowed fields
- writes manifest only when meaningful drift exists
- exits successfully when no drift exists

Files/components affected:
- src/doc_sync/sync.py
- src/doc_sync/orchestrator.py

Dependencies:
- P1-05 through P1-12

Expected outcome:
The full synchronization flow runs in a safe, deterministic, and repeatable manner.

Testing required:
- integration tests
- no-op behavior tests
- golden/snapshot validation

Blocked:
No

### Task ID: P1-14
Priority: High
Task description:
Implement manual CLI execution support if required by the architecture. This ensures the tool can be run locally for testing and validation without depending on GitHub Actions.

Files/components affected:
- src/doc_sync/cli.py
- pyproject.toml

Dependencies:
- P1-13

Expected outcome:
A human can run the synchronization logic locally and inspect the generated manifest or the diff.

Testing required:
- CLI smoke tests
- dry-run or no-drift checks

Blocked:
No

### Task ID: P2-15
Priority: Medium
Task description:
Create unit tests covering extraction, normalization, secret filtering, field protection, missing-value handling, and drift detection.

Files/components affected:
- tests/unit/

Dependencies:
- P1-05 through P1-13

Expected outcome:
Core logic is validated in isolation and behaves correctly under expected and edge-case conditions.

Testing required:
- unit test suite execution
- coverage check for critical logic

Blocked:
No

### Task ID: P2-16
Priority: Medium
Task description:
Create integration tests covering end-to-end manifest synchronization behavior using controlled repository fixtures.

Files/components affected:
- tests/integration/

Dependencies:
- P1-13
- P1-14
- P2-15

Expected outcome:
The full repository-to-manifest synchronization flow works without modifying unrelated files and preserves protected fields.

Testing required:
- integration test suite execution

Blocked:
No

### Task ID: P2-17
Priority: Medium
Task description:
Create golden/snapshot tests to validate deterministic output, manifest formatting, and stable field updates.

Files/components affected:
- tests/golden/
- tests/snapshots/

Dependencies:
- P1-09
- P1-11
- P2-16

Expected outcome:
The manifest output is stable for a given repository state, and formatting remains consistent with Technical-App-Manifest-v1.

Testing required:
- golden/snapshot test execution
- diff verification against expected output

Blocked:
No

### Task ID: P2-18
Priority: Medium
Task description:
Implement the GitHub Actions workflow to run the synchronization automation, verify diff, commit only when a real change exists, and avoid recursive self-triggering.

Files/components affected:
- .github/workflows/sync-manifest.yml

Dependencies:
- P1-13
- P1-14
- P2-16
- P2-17

Expected outcome:
The automation runs in CI, updates the manifest only when needed, and skips automation-generated commits to prevent loops.

Testing required:
- workflow validation in CI
- recursive-trigger prevention tests
- no-op commit tests

Blocked:
No

### Task ID: P2-19
Priority: Medium
Task description:
Implement explicit error-handling and safe-failure behavior across repository scanning, extraction, manifest parsing, and writing. This task is also used as a consolidation and verification step for component-level error handling.

Files/components affected:
- src/doc_sync/errors.py
- src/doc_sync/sync.py
- src/doc_sync/manifest_update.py
- relevant component modules

Dependencies:
- P1-05 through P1-13

Expected outcome:
Failures are visible, controlled, and safe. The manifest is never partially written when the intermediate state is invalid.

Testing required:
- unit tests for error states
- integration tests for malformed config and missing files
- final verification of safe-failure behavior

Blocked:
No

### Task ID: P2-20
Priority: Medium
Task description:
Perform final project verification: ensure all acceptance criteria, requirements, and architecture constraints are satisfied before considering the implementation complete.

Files/components affected:
- test suite
- CI workflow
- release validation checklist

Dependencies:
- P2-15
- P2-16
- P2-17
- P2-18
- P2-19

Expected outcome:
The project passes the required validation gates and is ready for a final review against the approved architecture and requirements.

Testing required:
- full test suite execution
- CI validation
- diff review for manifest safety

Blocked:
No

## 5. Notes on Implementation Scope

The implementation remains intentionally small and practical:

- one Python project with internal modules
- no separate services or applications
- no unnecessary framework abstraction
- no broad infrastructure beyond the required GitHub Actions workflow
- modular structure only where it provides clear implementation value

This keeps the project aligned to the approved architecture and the capstone constraints while maintaining readability, testability, and maintainability.
