# Design Review

## 1. Review Objective

This architecture was reviewed against the approved user story and requirements before implementation to confirm that the design was sufficiently complete, safe, and aligned to the project constraints.

The review focused on requirements coverage, implementation feasibility, safety, determinism, automation behavior, and the risk of incorrect documentation updates before any source code was implemented.

## 2. Artifacts Reviewed

The following artifacts were reviewed:

- user-story.md
- requirements.md
- architecture.md

## 3. Findings

### Finding ID: ARCH-01
Severity: Medium

Problem:
The architecture described metadata extraction and allowed source files, but it did not define the exact mapping from repository artifacts to each required manifest field.

Impact:
Without a defined field-to-source mapping, different developers could interpret the same requirement differently, leading to inconsistent metadata extraction and unstable manifest output.

Resolution:
Add an explicit field catalog that maps each repository-derived field to:
- authoritative source
- extraction method
- normalization rule
- fallback behavior

Status:
Resolved in architecture.md by adding the field-to-source mapping section.

### Finding ID: ARCH-02
Severity: High

Problem:
The architecture described reading and parsing the Markdown manifest, but it did not define a safe method for updating it without corrupting formatting or overwriting human-maintained content.

Impact:
A naive write strategy could corrupt the Markdown structure or overwrite narrative content, risking non-compliance with the preservation requirements.

Resolution:
Use section-aware, field-level Markdown updates instead of regenerating the entire document. Only explicitly targeted technical fields should be updated while preserving all other text, headings, ordering, and formatting.

Status:
Resolved in architecture.md by defining field-scoped updates and manifest preservation rules.

### Finding ID: ARCH-03
Severity: High

Problem:
The architecture noted that human-maintained fields must be preserved, but it did not specify a clear allowlist/blocklist enforcement model.

Impact:
If the synchronization logic is too broad, it could overwrite fields such as Service Owner, Business Impact, Description, JIRA Board, and On-Call Rotation, which are explicitly protected.

Resolution:
Maintain an explicit allowlist of repository-derived technical fields that may be updated and a protected blocklist of human-maintained fields that must never be modified. Validate the proposed change set before writing the manifest.

Status:
Resolved in architecture.md by adding explicit allowlist and protected field rules.

### Finding ID: ARCH-04
Severity: High

Problem:
The architecture identified the need to avoid secret exposure, but it did not define concrete secret handling rules and detection patterns.

Impact:
Sensitive values could be unintentionally written into the generated manifest, creating a direct security and compliance risk.

Resolution:
Define a concrete filtering policy that treats values associated with names such as SECRET, PASSWORD, TOKEN, API_KEY, CREDENTIAL, PRIVATE_KEY, and similar credential patterns as sensitive. Environment variable names may be documented, but their values must never be written. If a field is excluded because it is sensitive, the field should be represented as Not Found where the field contract requires a value.

Status:
Resolved in architecture.md by adding explicit secret filtering and Not Found handling rules.

### Finding ID: ARCH-05
Severity: Medium

Problem:
The architecture said missing technical values should be written as Not Found, but it did not distinguish clearly between missing values, empty values, sensitive values intentionally excluded, parse failures, and invalid repository state.

Impact:
Without clear semantics, the implementation could silently misclassify invalid or filtered data as acceptable output, reducing trust in the generated manifest.

Resolution:
Define these behaviors explicitly:
- Missing/unavailable metadata → Not Found
- Empty technical value → Not Found where applicable
- Secret/sensitive value → never write the value
- Parse failure or unreadable authoritative configuration → report explicit error and do not write a partially generated manifest

Status:
Resolved in architecture.md by adding missing, invalid, and sensitive-value handling rules.

### Finding ID: ARCH-06
Severity: High

Problem:
The architecture did not define error handling for missing files, unreadable files, malformed configuration, malformed manifests, unsupported repository states, failed metadata extraction, or failed manifest updates.

Impact:
Unknown or partial failure states could produce inconsistent or unsafe generated documentation.

Resolution:
Define explicit failure behavior that reports an error and prevents the manifest from being written if the intermediate metadata state is invalid or the update process fails.

Status:
Resolved in architecture.md by adding an explicit error-handling section.

### Finding ID: ARCH-07
Severity: Medium

Problem:
The architecture described drift detection, but it did not specify normalized comparison rules for values before determining drift.

Impact:
Without normalization, formatting differences, list ordering differences, or casing inconsistencies could cause false drift and unnecessary manifest change events.

Resolution:
Normalize both extracted metadata and manifest values before comparison. Use stable ordering for lists and consistent whitespace and formatting rules. Determine drift field-by-field after normalization.

Status:
Resolved in architecture.md by adding normalization and comparison rules.

### Finding ID: ARCH-08
Severity: High

Problem:
The architecture described recursion prevention but did not specify one concrete workflow control mechanism to stop an endless synchronization loop.

Impact:
Without a concrete guard, a committed manifest update could retrigger the workflow indefinitely, creating a commit loop and unstable CI behavior.

Resolution:
Use a concrete anti-recursion mechanism: detect the automation-generated commit and skip synchronization for that commit.

Status:
Resolved in architecture.md by defining the specific GitHub Actions recursion protection mechanism.

### Finding ID: ARCH-09
Severity: Medium

Problem:
The architecture did not define the exact no-op behavior for a run with no drift.

Impact:
A workflow could still create a commit or modify the manifest even when there is no technical change, violating the requirement that the manifest remain unchanged and the process exit successfully.

Resolution:
If no drift exists:
- do not modify the manifest
- do not create a commit
- exit successfully

If drift exists:
- update only allowed technical fields
- update Last Updated
- verify the resulting diff
- commit only when an actual change exists

Status:
Resolved in architecture.md by adding explicit no-op and drift behavior.

### Finding ID: ARCH-10
Severity: Medium

Problem:
The architecture included test categories but did not specify a concrete test matrix to validate the most important project guarantees.

Impact:
Critical behaviors such as protected-field preservation, secret filtering, deterministic output, idempotence, and CI recursion protection might not be proven during implementation.

Resolution:
Define an explicit test matrix covering:
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

Status:
Resolved in architecture.md by adding the concrete CI and test matrix requirements.

### Finding ID: ARCH-11
Severity: Medium

Problem:
The architecture was directionally correct, but it did not fully describe maintainability boundaries for the metadata extraction and synchronization logic as the project grows.

Impact:
Without a clear modular structure, the logic could become brittle and hard to extend while still meeting the fixed template and limited scope requirements.

Resolution:
Use a simple modular structure with:
- metadata extraction
- normalization
- manifest parsing/updating
- drift detection
- synchronization orchestration

This keeps the solution maintainable without introducing separate services or applications.

Status:
Resolved in architecture.md by retaining a practical modular structure within a single Python application.

## 4. Architecture Changes Made

The following concrete changes were made to architecture.md as a result of the review:

1. Added a field-to-source mapping table for all repository-derived manifest fields.
2. Clarified that manifest updates are section-aware and field-level only.
3. Added an explicit allowlist for synchronized technical fields and a blocklist for protected human-maintained fields.
4. Added a concrete secret filtering policy using sensitive name patterns and value protection rules.
5. Added explicit behavior for missing, empty, sensitive, and invalid metadata values.
6. Added a normalization and drift comparison section to ensure deterministic comparisons.
7. Added a concrete recursion prevention rule for GitHub Actions.
8. Added explicit no-op behavior when there is no drift.
9. Added explicit error-handling requirements for invalid intermediate states.
10. Added a concrete test matrix to validate extraction, drift detection, and GitHub Actions safety.
11. Added a deterministic Last Updated format requirement using UTC ISO-8601.
12. Kept the solution practical for a small Python project without introducing unnecessary services or infrastructure.

## 5. Final Design Decisions

The following decisions were approved and documented for implementation:

- Repository code and technical configuration are the source of truth.
- The manifest is a Markdown file at docs/technical-app-manifest.md.
- The manifest follows the Technical-App-Manifest-v1 structure.
- The solution performs field-level updates only and does not regenerate the whole document.
- Human-maintained fields are protected and never overwritten.
- Missing technical values are represented as Not Found.
- Secret values are never written to the manifest.
- Sensitive values associated with names such as SECRET, PASSWORD, TOKEN, API_KEY, CREDENTIAL, and PRIVATE_KEY are filtered before writing.
- Environment variable names may be documented, but their values are never written.
- Repository-derived technical fields are synchronized; non-technical content is preserved.
- Drift detection is based on normalized field-by-field comparisons.
- The synchronization process is deterministic and idempotent.
- GitHub Actions performs the automated synchronization.
- The workflow prevents recursive self-triggering by skipping automation-generated commits.
- Last Updated uses UTC ISO-8601 format and is updated only when actual technical changes are synchronized.
- Testing includes unit, integration, golden/snapshot, and CI validation coverage.

## 6. Accepted Risks and Limitations

Only the risks and limitations that were actually identified during the review are included below:

1. The implementation will depend on the availability and quality of authoritative repository configuration files.
2. If an authoritative configuration file is unreadable or malformed, the workflow must fail safely and not produce a partial manifest.
3. The project depends on precise secret filtering rules to prevent sensitive values from appearing in the generated documentation.
4. The GitHub Actions recursion guard must be implemented carefully to avoid infinite synchronization loops.
5. The manifest update logic must remain field-scoped and deterministic to preserve human-maintained sections and formatting.

## 7. Review Status

Status: Approved for Implementation

The architecture review findings were addressed as documented, and the approved design is ready for implementation.
